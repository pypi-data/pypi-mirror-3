# Author: Jacob Smullyan <jsmullyan@gmail.com>
# Copyright 2007 WNYC New York Public Radio

from structure import ADUFORMAT
from datatypes import from_adu

def _readline(line):
    for field in ADUFORMAT:
        datatype, start, end= field[3:6]
        start-=1
        fieldname=field[0]
        value=line[start:end]
        yield (fieldname, datatype, value)

def _read_adu(fp):
    makedict=lambda line: dict((name.strip(),
                                from_adu(datatype, value))
                               for name, datatype, value
                               in _readline(line))
    def chomp(line):
        if (not line) or line[-1]!='\n':
            return line
        return line[:-1]

    getchomped=(x for x in (chomp(line) for line in fp) if x)
    return (makedict(chomped) for chomped in getchomped)

    

if __name__=='__main__':
    import sys
    for fname in sys.argv[1:]:
        data=_read_adu(open(fname))
        print "file: %s" % fname
        for d in data:
            print '------------'
            for k in sorted(d):
                v=d[k]
                if v not in ('', None):
                    print "%s: %s" % (k, v)
            
        
            
            


    
        

