#!/usr/local/bin/python

import re
import sys

from obitools.fasta import formatFasta,fastaIterator
from obitools.options import getOptionManager
from obitools.utils import ColumnFile, deprecatedScript
from obitools.fast import Fast
from obitools import NucSequence


def addSplitOptions(optionManager):
    
    optionManager.add_option('-p','--prefix',
                             action="store", dest="prefix",
                             metavar="<PREFIX FILENAME>",
                             type="string",
                             default=None,
                             help="sequence of the direct primer")


    optionManager.add_option('-t','--tag-name',
                             action="store", dest="tagname",
                             metavar="<tagname>",
                             type="string",
                             default=None,
                             help="file containing tag used")
    
    optionManager.add_option('-u','--undefined',
                             action="store", dest="undefined",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file used to store unidentified sequences")
    
def outputFile(seq,options):
    if options.tagname is None:
        name = seq.id
    else:
        if options.tagname in seq:
            name = seq[options.tagname]
        else:
            name=None
    if name is None:
        if options.undefined is not None:
            file = open(options.undefined,'a')
        else:
            file = None
    else:
        if options.prefix is not None:
            name = '%s%s' % (options.prefix,name)
        file = open('%s.fasta' % name,'a')
    return file

if __name__=='__main__':
    
    deprecatedScript('obisplit')
    
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addSplitOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()
    
    for seq in entries:
        f = outputFile(seq, options)
        if f is not None:
            print >>f,formatFasta(seq)
            del f
            
            
    
    
    
