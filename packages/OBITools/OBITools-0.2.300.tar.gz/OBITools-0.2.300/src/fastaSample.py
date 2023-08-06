#!/usr/local/bin/python
'''
Created on 1 nov. 2009

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.fasta import fastaIterator,formatFasta
from obitools.sample import weigthedSample
from obitools.utils import deprecatedScript

def addSampleOptions(optionManager):
    optionManager.add_option('-s','--sample-size',
                             action="store", dest="size",
                             metavar="###",
                             type="int",
                             default=None,
                             help="Size of the generated sample"
                             )
 


if __name__ == '__main__':
    
    deprecatedScript('obisample')

    optionParser = getOptionManager([addSampleOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()
    
    db = [s for s in entries]
    
    if options.size is None:
        options.size=len(db)
        
    distribution = {}
    idx=0
    
    for s in db:
        if 'count' in s:
            count = s['count']
        else:
            count = 1
        distribution[idx]=count
        idx+=1
        
    sample =weigthedSample(distribution, options.size)
    
    for idx in sample:
        seq = db[idx]
        seq['count']=sample[idx]
        print formatFasta(seq)
        
        

