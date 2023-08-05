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
import sys

try:
    import xml.etree.cElementTree as X
except ImportError:
    import xml.etree.ElementTree as X

from objects import ADURecord
from structure import ADUFORMAT


# There are probably other numeric fields
NUMERIC_ADU_FORMAT = [field for field in ADUFORMAT if field[3] in ('NUMBER',)]


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


def yield_converted_from_excel_xml(xmlpath, cellmap, extra=None):
    # print >> sys.stderr, cellmap, extra
    ns = '{urn:schemas-microsoft-com:office:spreadsheet}'
    doc = X.parse(open(xmlpath))
    rows = doc.findall('//%sRow' % ns)
    headerrow = rows[0]
    celltag = '%sCell/%sData' % (ns, ns)
    headernames = [x.text for x in headerrow.findall(celltag)]
    # print >> sys.stderr, headernames
    for row in rows[1:]:
        valuedict = dict(zip(headernames,
                             [x.text for x in row.findall(celltag)]))
        # print >> sys.stderr, valuedict
        renamed = dict((k, valuedict.get(v)) for k, v in cellmap.items())
        # print >> sys.stderr, renamed
        strings_to_ints(renamed)
        # print >> sys.stderr, renamed
        adu = ADURecord()
        if extra:
            adu.update(extra)
        adu.update(renamed)
        yield adu


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
        for record in yield_converted_from_excel_xml(f, cellmap, extra):
            records.append(record)
    ADURecord.to_file(records, output)
    output.close()

            
if __name__ == '__main__':
    main(sys.argv[1:])
