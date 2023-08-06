#!/usr/local/bin/python
'''
Created on 15 dec. 2009

@author: coissac
'''
from obitools.fasta import fastaIterator,formatFasta
from obitools.options import getOptionManager

import sys
from obitools.utils import deprecatedScript

def addHeadOptions(optionManager):
    optionManager.add_option('-n','--sequence-count',
                             action="store", dest="count",
                             metavar="###",
                             type="int",
                             default=10,
                             help="Count of first sequences to print")
    

if __name__ == '__main__':
    
    deprecatedScript('obihead')
    
    optionParser = getOptionManager([addHeadOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()
    i=0
    
    for s in entries:
        if i < options.count:
            print formatFasta(s)
            i+=1
        else:
            sys.exit(0)
            
        

