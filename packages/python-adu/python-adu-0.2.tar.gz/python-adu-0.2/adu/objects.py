# Author: Jacob Smullyan <jsmullyan@gmail.com>
# Copyright 2007 WNYC New York Public Radio

import cStringIO

from generator import _tolist, _writeline
from parser import _read_adu
from structure import ADUFORMAT

class ADURecord(object):
    """
    a class representing a single ADU record.

    Individual fields can be accessed by attribute.  Attribute names
    are the same as ADU names, but with spaces replaced by
    underscores: 'First_Name_1' rather than 'First Name 1', etc.

    These objects can be created from scratch and manually populated with data:

    >>> r=ADURecord()
    >>> r.First_Name_1=u"Mary"
    >>> r.Last_Name_1=u"Ferguson"
    >>> r.update({'Middle_Name_1' : u'Beatrice', 'City' : u'Brooklyn'})

    or by reading it from a file:

    >> records=ADURecord.from_file('somefile.txt')

    Once created, they can be written to a file in ADU format:

    >> ADURecord.to_file(records, 'anotherfile.txt')

    """
    def __init__(self, data=None):
        d=self.__dict__['_data']={}
        if data:
            # support for cloning another record object
            d.update(getattr(data, '_data', data))
        for rec in ADUFORMAT:
            d.setdefault(rec[0], None)

    def update(self, data):
        if hasattr(data, '_data'):
            d=data._data
        else:
            d=dict((k.replace('_', ' '), v) for k,v in data.iteritems())
        self._data.update(d)

    def __getattr__(self, k):
        nk=k.replace('_', ' ')
        try:
            return self._data[nk]
        except KeyError:
            raise AttributeError, "no such attribute: %s" % k

    def __setattr__(self, k, v):
        nk=k.replace('_', ' ')
        if nk in self._data:
            self._data[nk]=v
        else:
            super(ADURecord, self).__setattr__(k, v)
        
    @classmethod
    def from_file(cls, filename):
        """
        given the name of a file containing ADU records, returns a list of ADURecord objects.
        """
        return [cls(x) for x in _read_adu(open(filename))]

    @staticmethod
    def to_file(records, file):
        """
        writes the data given in a list of ADURecord objects to the given filename or file.
        """
        havefile=hasattr(file, 'write')
        if havefile:
            # assume it is a file
            fp=file
        else:
            fp=open(file, 'wb')
        for r in records:
            _writeline(fp, r._data)
        if not havefile:
            fp.close()
        else:
            fp.flush()

    def to_string(self):
        sio=cStringIO.StringIO()
        _writeline(sio, self._data)
        return sio.getvalue()

    def to_list(self):
        return _tolist(self._data)

    def get_summary(self):
        """
        a convenience method for debugging that returns the data in the record which is not null.
        """
        return dict((k, v) for k, v in self._data.iteritems() if v != None)
                        

if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:
        print >> sys.stderr, "usage: %s filename" % sys.argv[0]
        sys.exit(1)
    filename=sys.argv[1]
    recs=ADURecord.from_file(filename)
    for idx, rec in enumerate(recs):
        if idx > 0:
            print '-------'
        for k, v in sorted(rec.get_summary().iteritems()):
            print "%s: %s" % (k, v)
    

        
