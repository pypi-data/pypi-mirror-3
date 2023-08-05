#! /usr/bin/env python
"""
this command-line utility will convert some xml files from excel,
found in the field, into rows of data that can be mapped to an ADU
file according to a provided mapping.  Extra data can also be provided
on the command line to include in the file.

No guarantee of universality obtains, and if the document cannot be
parsed, or there is no data, this will bomb out.
"""

import optparse
import os
import re
import sys

try:
    import xml.etree.cElementTree as X
except ImportError:
    import xml.etree.ElementTree as X

from objects import ADURecord
from structure import ADUFORMAT


# There are probably other numeric fields
NUMERIC_ADU_FORMAT = [field for field in ADUFORMAT if field[3] in ('NUMBER',)]
NS = '{urn:schemas-microsoft-com:office:spreadsheet}'
CELL_TAG = NS + 'Cell'
INDEX_ATTRIB = NS + 'Index'
DATA_TAG = NS + 'Data'


def strings_to_ints(adu_record):
    """Modifies adu_record."""
    for field in NUMERIC_ADU_FORMAT:
        name = field[0]
        try:
            adu_record[name] = int(adu_record[name])
        except KeyError:
            pass # every record doesn't have every field
        except TypeError, error:
            print >> sys.stderr, "%s. Field %s, value %s." % (error, name, adu_record[name])


def yield_converted_from_excel_xml(xmlpath, cellmap, extra=None,
                                   digits_col=None,
                                   truncate_long_values=False):
    """Pass a column header as digits_col to strip non-digits from data in
    that column."""
    # print >> sys.stderr, cellmap, extra
    print >> sys.stderr, "Opening and parsing file."
    doc = X.parse(open(xmlpath))
    print >> sys.stderr, "Collecting all the rows."
    rows = doc.findall('//%sRow' % NS)
    headernames = _get_row_text(rows[0])
    # print >> sys.stderr, headernames
    if digits_col is not None:
        digits_col_i = _col_name_to_index(headernames, digits_col)
    print >> sys.stderr, "Converting."
    for line_num, row in enumerate(rows[1:], 2):
        try:
            row_text = _get_row_text(row)
            missing_end_cols = [''] * (len(headernames) - len(row_text))
            full_row_text = row_text + missing_end_cols
            # print >> sys.stderr, full_row_text
            if digits_col is not None:
                full_row_text[digits_col_i] = re.sub(r'[^0-9]', '',
                                                     full_row_text[digits_col_i])
            # print >> sys.stderr, full_row_text
            valuedict = dict(zip(headernames, full_row_text))
            # print >> sys.stderr, valuedict
            renamed = {}
            for cellname, aduname in cellmap.items():
                renamed[aduname] = valuedict.get(cellname)
            # print >> sys.stderr, renamed
            strings_to_ints(renamed)
            # print >> sys.stderr, renamed
            adu = ADURecord()
            if extra:
                adu.update(extra)
            adu.update(renamed)
            # Call to_list() to do validation now instead of waiting to get
            # errors when writing output. This does mean to_list() is called
            # twice for each record.
            adu.to_list(truncate_long_values)
            yield adu
        except Exception, error:
            print >> sys.stderr, "Error on line %s: %s" % (line_num, error)


def _get_row_text(excel_xml_row_elem):
    """Returns a list of strings. It won't contain empty items for empty cells
    after the last cell with something in it."""
    res = []
    for cell in excel_xml_row_elem.findall(CELL_TAG):
        # print >> sys.stderr, cell.attrib
        if INDEX_ATTRIB in cell.attrib:
            up_to_col = len(res) + 1
            cell_index = int(cell.attrib[INDEX_ATTRIB])
            # print >> sys.stderr, ("up to col: %s, cell index: %s" %
            #                       (up_to_col, cell_index))
            if cell_index < up_to_col:
                raise NotImplemented
            elif cell_index > up_to_col:
                skip_cols = cell_index - up_to_col
                # print >> sys.stderr, "Skipping %s columns." % skip_cols
                res.extend([''] * skip_cols)
        data = cell.findall(DATA_TAG)[0]
        res.append(data.text)
    return res


def _col_name_to_index(headers, col_name):
    for col in enumerate(headers):
        if col[1] == col_name:
            return col[0]
    raise ValueError("Col '%s' not found" % col_name)


def main(args):
    usage="%prog [options] file [files...]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-c',
                      '--cell',
                      dest='cells',
                      action='append',
                      help=('add a mapping of a spreadsheet '
                            'cell name to an ADU field name, '
                            'in cellname:aduname format'))
    parser.add_option('-x',
                      '--extra',
                      dest='extra',
                      action='append',
                      help='extra key:value pairs to add to the ADU')
    parser.add_option('-o',
                      '--output',
                      dest='output',
                      default='-',
                      help="where to write the ADU file (default: stdout)")
    parser.add_option('-d',
                      '--digit-col',
                      dest='digit_col',
                      default=None,
                      help="original name of column to strip non-digits from")
    parser.add_option('-t',
                      '--truncate-long',
                      action='store_true',
                      dest='truncate_long_values',
                      default=False,
                      help=("truncate too long values instead of skipping "
                            "those records"))
    opts, args = parser.parse_args(args)
    if not args:
        parser.error('expected an input file')
    if not opts.cells:
        parser.error('you must specify some mapping to use')
    if not all(c.count(':') == 1 for c in opts.cells):
        parser.error('cell format should be "cellname:aduname"')
    if opts.extra and not all (c.count(':') == 1 for c in opts.extra):
        parser.error('extra data format should be "key:value"')
    cellmap = dict(c.split(':') for c in opts.cells)
    extra = dict(c.split(':') for c in opts.extra) if opts.extra else {}
    if opts.output == '-':
        output = sys.stdout
    else:
        if os.path.exists(opts.output):
            parser.error('output file %s already exists, exiting' % opts.output)
        output = open(opts.output, 'wb')
    records = []
    for f in args:
        for record in yield_converted_from_excel_xml(f, cellmap, extra,
                                                     opts.digit_col,
                                                     opts.truncate_long_values):
            records.append(record)
    print >> sys.stderr, "Writing adu records to output file."
    ADURecord.to_file(records, output, opts.truncate_long_values)
    output.close()


if __name__ == '__main__':
    main(sys.argv[1:])
