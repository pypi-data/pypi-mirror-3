#!/usr/local/bin/python
'''
Created on 17 mars 2011

@author: coissac
'''

from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from random import normalvariate, uniform
from obitools.location import locationGenerator
import math

def addNGSSimOptions(optionManager):
    
    optionManager.add_option('-l','--length',
                             action="store", dest="length",
                             metavar="###",
                             type="int",
                             default=500,
                             help="fragment length")

    optionManager.add_option('-v','--length-var',
                             action="store", dest="var",
                             metavar="###.##",
                             type="float",
                             default=10.,
                             help="fragment length variance")


    optionManager.add_option('-r','--read-length',
                             action="store", dest="reads",
                             metavar="###",
                             type="int",
                             default=100,
                             help="sequencer read length")
      
    optionManager.add_option('-c','--coverage',
                             action="store", dest="coverage",
                             metavar="###.##",
                             type="float",
                             default=10,
                             help="sequencing depth")
    
    optionManager.add_option('-C','--circular',
                             action="store_true", dest="circular",
                             default=False,
                             help="sequences are circular")
    
    optionManager.add_option('-e','--reading-error',
                             action="store", dest="error",
                             metavar="###.##",
                             type="float",
                             default=0,
                             help="sequencing error rate")
    
    optionManager.add_option('-p','--pair-end',
                             action="store", dest="pairend",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="File containing the reverse reads")
    
def fragments(options,seq):
    lseq   = len(seq)
    covmax = lseq * options.coverage
    cov    = 0
    
    while cov < covmax :
        length = int(math.floor(normalvariate(options.length,options.var)))
        
        if options.circular :
            pos = int(math.floor(uniform(0,lseq-1)))
            f1 = min(length,lseq - pos)
            f2 = length - f1
            
            if f2==0:
                frg = seq[pos:pos+length]
            else:
                loc = locationGenerator('join(%d..%d,%d..%d)' % (pos+1,pos+f1,
                                                                1,f2))
                frg = seq[loc]
            
        else:
            pos = int(math.floor(uniform(0,len(seq)-length)))
            frg = seq[pos:pos+length]
    
        if options.reads < length:
            f1 = frg[0:options.reads]
            cov+=len(f1)
            
            if options.pairend is not None:
                f2 = frg[-options.reads:].complement()
                cov+=len(f2)
                rep=(f1,f2)
            else:
                rep=(f1,)
        else:
            rep = (frg,)                
            cov+=len(frg)
            
        yield rep

if __name__ == '__main__':
    optionParser = getOptionManager([addNGSSimOptions,addInOutputOption])
    
    (options, entries) = optionParser()

    writer = sequenceWriterGenerator(options)

    if options.pairend is not None:
        pairend = sequenceWriterGenerator(options,open(options.pairend,"w"))
    else :
        pairend = None
        
    for seq in entries:
        for f in fragments(options,seq):
            writer(f[0])
            if pairend is not None:
                pairend(f[1])
            
   
