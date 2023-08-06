#!/usr/local/bin/python
'''
Created on 1 nov. 2009

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.fasta import fastaIterator
from obitools.utils import deprecatedScript

def addCountOptions(optionManager):
    optionManager.add_option('-s','--sequence',
                             action="store_true", dest="sequence",
                             default=False,
                             help="Print the count of differentes sequences"
                             )
 
    optionManager.add_option('-a','--all',
                             action="store_true", dest="all",
                             default=False,
                             help="Print the count of all sequences"
                             )


if __name__ == '__main__':
    
    deprecatedScript('obicount')
    
    optionParser = getOptionManager([addCountOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()
    
    count1=0
    count2=0
    
    for s in entries:
        count1+=1
        if 'count' in s:
            count2+=s['count']
        else:
            count2+=1
            
    if options.all==options.sequence:
        print count1,count2
    elif options.all:
        print count2
    else:
        print count1
        