#!/usr/local/bin/python

from obitools.fasta import fastaIterator,formatFasta
from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import sequenceFilterIteratorGenerator
from obitools.utils import deprecatedScript


if __name__=='__main__':
    
    deprecatedScript('obigrep')
    
    optionParser = getOptionManager([addSequenceFilteringOptions],
								    entryIterator=fastaIterator)
    
    (options, entries) = optionParser()
        
    goodSeq   = sequenceFilterIteratorGenerator(options)
    
    for seq in goodSeq(entries):
        print formatFasta(seq)
            
            