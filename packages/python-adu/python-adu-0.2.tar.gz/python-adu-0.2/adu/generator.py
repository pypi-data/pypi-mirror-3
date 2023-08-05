# Author: Jacob Smullyan <jsmullyan@gmail.com>
# Copyright 2007 WNYC New York Public Radio

from structure import ADUFORMAT
from datatypes import to_adu

def _writeline(fp, data):
    for value in _tolist(data):
        fp.write(value)
    fp.write('\n')


def _tolist(data):
    res = []
    for field in ADUFORMAT:
        name = field[0]
        length, datatype = field[2:4]
        value = to_adu(datatype, data.get(name), length)
        value = value.rjust(length)
        if len(value) != length:
            raise ValueError(
                "value too long for field %s (expected %d): %s" \
                % (name, length, value))
        res.append(value)
    return res
