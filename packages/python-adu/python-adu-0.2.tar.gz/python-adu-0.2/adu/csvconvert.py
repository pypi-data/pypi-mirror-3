#!/usr/bin/env python

import csv

import datatypes
from objects import ADURecord
from structure import ADUFORMAT


_ADUFORMAT_BY_FIELD = dict([(x[0], x) for x in ADUFORMAT])


def write_csv(adu_records, fp):
    """fp can be anything that implements write()."""
    writer = csv.writer(fp)
    writer.writerow([x[0] for x in ADUFORMAT])
    for item in adu_records:
        writer.writerow(item.to_list())


def read_csv(fp):
    """
    Reads a csv file and returns a list of ADURecords.
    
    All ADU fields must be in the file and they must be in the correct order.
    
    fp can be anything that implements read().
    """
    reader = csv.reader(fp)
    adus = []
    headings = []
    for record in reader:
        if not headings: # read first record into headings
            headings = [h.strip() for h in record if h.strip() != '']
            for format_field, csv_field in zip(ADUFORMAT, headings):
                if format_field[0] != csv_field:
                    raise Exception(
                        "CSV field '%s' doesn't match the adu format." %
                        csv_field)
        else:
            adu_record = ADURecord()
            for field, value in zip(headings, record):
                datatype = _ADUFORMAT_BY_FIELD[field][3]
                adu_val = datatypes.from_adu(datatype, value)
                setattr(adu_record, field, adu_val)
            adus.append(adu_record)
    return adus


if __name__ == '__main__':
    # For testing, pass it a csv file. It will parse it and then recreate it
    # and make sure the new file is the same and the original.
    import subprocess
    import sys
    
    orig = open(sys.argv[1])
    adus = read_csv(orig)
    orig.close()
    new_name = sys.argv[1] + '-out.csv'
    new = open(new_name, 'w')
    write_csv(adus, new)
    new.close()
    if subprocess.call(['diff', '-q', sys.argv[1], new_name]) != 0:
        print "Round trip conversion changed info."
