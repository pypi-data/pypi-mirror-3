#!/usr/local/bin/python


import fileinput
import re
import getopt
import sys

from obitools.fasta import fastaIterator,formatFasta 
from obitools.fast import Fast
           
def strandOnRefGenerator(seqref,kup=2):
    hashd = Fast(seqref,kup)
    hashr = Fast(seqref.complement(),kup)
    
    def isDirect(seq):
        sdirect,p =hashd(seq)
        sreverse,p=hashr(seq)
        return sdirect > sreverse,sdirect,sreverse
	
    return isDirect    
    
def printHelp():
    print "-----------------------------------"
    print " fastaGrep.py"
    print "-----------------------------------"
    print "fastaGrep.py [option] <argument>"
    print "-----------------------------------"
    print "-h    --help                       : print this help"
    print "-r    --reference=<fasta>          : fasta file containing reference sequence"
    print "-k    --kup=##                     : word size used in fastn algorithm"
    print "-----------------------------------"
    

if __name__=='__main__':

    o,filenames = getopt.getopt(sys.argv[1:],
                                'hr:k:',
                                ['help',
                                 'reference=',
                                 'kup:'])
                                 
    kup = 6
    
    sys.argv[1:]=filenames
    
    for name,value in o:
        if name in ('-h','--help'):
            printHelp()
            exit()
            
        elif name in ('-r','--reference'):
            rseq=fastaIterator(value).next()
            
        elif name in ('-k','--kup'):
            kup = int(value)
            
        else:
            raise ValueError,'Unknown option %s' % name
    
                                 
    isDirect=strandOnRefGenerator(rseq,kup)
    
    fasta = fastaIterator(fileinput.input())
    rid=rseq.id
    
    for seq in fasta:
            d,ds,rs=isDirect(seq)
            seq['isDirect']=str(d)
            seq['directScore']=str(ds)
            seq['reverseScore']=str(rs)
            seq['onReference']=rid
            print formatFasta(seq)
            
            