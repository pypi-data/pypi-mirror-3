# Author: Jacob Smullyan <jsmullyan@gmail.com>
# Copyright 2007 WNYC New York Public Radio

import sys

from structure import ADUFORMAT
from datatypes import to_adu

def _writeline(fp, data, truncate_long_values=False):
    for value in _tolist(data, truncate_long_values):
        fp.write(value)
    fp.write('\n')


def _tolist(data, truncate_long_values=False):
    res = []
    for field in ADUFORMAT:
        name = field[0]
        length, datatype = field[2:4]
        value = to_adu(datatype, data.get(name), length)
        if truncate_long_values and len(value) > length:
            print >> sys.stderr, ("truncating too long value '%s' to '%s'" %
                                  (value, value[:length]))
            value = value[:length]
        # If I understand this all right, it's unnecessary to check the length
        # again if value's been truncated, but I'm paranoid about messing up
        # an ADU file so I'll leave it.
        value = value.rjust(length)
        if len(value) != length:
            raise ValueError(
                "value too long for field %s (expected %d): %s" \
                % (name, length, value))
        res.append(value)
    return res
