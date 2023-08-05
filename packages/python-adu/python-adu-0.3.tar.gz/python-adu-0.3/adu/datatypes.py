# Author: Jacob Smullyan <jsmullyan@gmail.com>
# Copyright 2007 WNYC New York Public Radio

import datetime
from decimal import Decimal
import re
import time


_dtpat=re.compile(r'^DATE(?:TIME)? (.+)$')

_dateformats={
    'adudatetime': (lambda x: x.strftime('%d-%b-%y%H:%M:%S').upper(),
                    lambda x: datetime.datetime(*time.strptime(x.title(), '%d-%b-%y%H:%M:%S')[:6]))
    }

# this is just a guess
ADU_ENCODING='windows-1252'

class InvalidADUFormatException(ValueError):
    pass

def to_adu(datatype, value, length):
    if value in (None, ''):
        # datatype doesn't matter
        return ''.rjust(length)

    if datatype=='BOOL':
        return 'NY'[bool(value)].rjust(length)
        
    elif datatype=='CHAR':
        if isinstance(value, unicode):
            return value.encode(ADU_ENCODING, 'replace').ljust(length)
        elif isinstance(value, str):
            return value.ljust(length)
        return str(value).ljust(length)

    elif datatype=='MONEY':
        # monetary values are stored in number of American cents.
        return  ("%d" % (value)).rjust(length)

    elif datatype=='NUMBER':
        return ("%d" % value).rjust(length)

    m=_dtpat.match(datatype)
    if m:
        format=m.group(1)
        try:
            formatter=_dateformats[format][0]
        except KeyError:
            return value.strftime(format).ljust(length)
        else:
            return formatter(value).ljust(length)
    

    else:
        raise ValueError, "unknown datatype: %s" % datatype



def from_adu(datatype, value):

    value=value.strip()
    if not value:
        return None

    if datatype=='NUMBER':
        return int(value)

    elif datatype=='MONEY':
        return Decimal(value)

    elif datatype=='BOOL':
        if value=='Y':
            return True
        elif value=='N':
            return False
        else:
            raise InvalidADUFormatException(
                "expected only 'Y', 'N', or blank for a BOOL field, got: '%s'" % value)

    elif datatype=='CHAR':
        return value.decode(ADU_ENCODING)

    m=_dtpat.match( datatype)
    if m:
        format=m.group(1)
        try:
            formatter=_dateformats[format][1]
        except KeyError:
            return datetime.datetime(*time.strptime(value, format)[:6])
        else:
            return formatter(value)

    else:
        raise ValueError, "unrecognized datatype: %s" % datatype
        
