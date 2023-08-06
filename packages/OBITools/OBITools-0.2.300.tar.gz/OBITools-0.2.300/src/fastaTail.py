#!/usr/local/bin/python
'''
Created on 15 dec. 2009

@author: coissac
'''
from obitools.fasta import fastaIterator,formatFasta
from obitools.options import getOptionManager
import collections
from obitools.utils import deprecatedScript

def addHeadOptions(optionManager):
    optionManager.add_option('-n','--sequence-count',
                             action="store", dest="count",
                             metavar="###",
                             type="int",
                             default=10,
                             help="Count of first sequences to print")
    

if __name__ == '__main__':
    
    deprecatedScript('obitail')
    
    optionParser = getOptionManager([addHeadOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()
    i=0
    
    queue = collections.deque(entries,options.count)
    
    while queue:
        print formatFasta(queue.popleft())
        
        
        

