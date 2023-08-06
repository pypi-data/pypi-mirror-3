#!/usr/local/bin/python

"""
   fastaLocate.py
"""

import fileinput
import getopt
import sys

from obitools.fasta import fastaIterator,formatFasta
from obitools.fast import Fast

from obitools.options import getOptionManager


def _probefile(options,opt,value,parser):
    seq = str(fastaIterator(value).next())
    parser.values.probe=seq


def addLocateOptions(optionManager):
    
    optionManager.add_option('-P','--probe-file',
                             action="callback", callback=_probefile,
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file name containing the oligo sequence")

    optionManager.add_option('-p','--probe',
                             action="store", dest="probe",
                             metavar="<DNA_SEQ>",
                             type="string",
                             default=None,
                             help="nucleic sequence of the probe to locate")

    optionManager.add_option('-k','--kup',
                             action="store", dest="kup",
                             metavar="##",
                             type="int",
                             default=2,
                             help="word size uses for aligment")

def locateRefGenerator(options):

                                 
    kup   = options.kup
    seqref= options.probe
    hashd = Fast(seqref,kup)

    def locate(seq):
        score,p =hashd(seq)
        seq['locate']=min(p)+1
        seq['locate_score']=score
        return seq
    
    return locate

if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addLocateOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()
    
    locator = locateRefGenerator(options)
    
    
    for seq in entries:
        info=locator(seq)          
        print formatFasta(seq)
    

