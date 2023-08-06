#!/usr/local/bin/python
'''
:py:mod:`solexaPairEnd` : align overlapping pair-end solexa reads and return the consensus sequence together with its quality
=============================================================================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`solexaPairEnd` aims at aligning the two reads of a pair-end library sequenced using a Solexa.

The program takes for arguments one or two fastq solexa sequences reads files. 

In the case where two files are given one should be associated with the -r option. Sequences corresponding to the same read pair must have the same line number in the two files.
In the case where one file is provided, sequences, which are supposed to be all of the same length, are considered to be the concatenation of the two pair end reads. Hence
the first half of a sequence is considered one extremity of the pair-end and the second half the other one.


:py:mod:`solexaPairEnd` align the first sequence with the reverse complement of the second sequence and report the consensus sequence of the alignment (taking into account
the base qualities) together with the qualities for each base of the reported consensus sequence.

.. code-block:: bash

   > solexaPairEnd -r seq3P.fasta seq5P.fasta > seq.fasta

'''

from obitools.options import getOptionManager
from obitools.fastq import fastqSolexaIterator, formatFastq
from obitools.align import QSolexaReverseAssemble
from obitools.align import QSolexaRightReverseAssemble
from obitools.tools._solexapairend import buildConsensus

from itertools import chain

def addSolexaPairEndOptions(optionManager):
    optionManager.add_option('-r','--reverse-reads',
                             action="store", dest="reverse",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="Filename containing reverse solexa reads "
                            )
    

def cutDirectReverse(entries):
    first = []
    
    for i in xrange(10):
        first.append(entries.next())
        
    lens = [len(x) for x in first]
    clen = {}
    for i in lens:
        clen[i]=clen.get(i,0)+1
    freq = max(clen.values())
    freq = [k for k in clen if clen[k]==freq]
    assert len(freq)==1,"To many sequence length"
    freq = freq[0]
    assert freq % 2 == 0, ""
    lread = freq/2
    
    seqs = chain(first,entries)
    
    for s in seqs:
        d = s[0:lread]
        r = s[lread:]
        yield(d,r)
    
def seqPairs(direct,reverse):
    for d in direct:
        r = reverse.next()
        yield(d,r)

def checkAlignOk(ali):
    #print not (ali[0][0]=='-' or ali[1][len(ali[1])-1]=='-')
    return not (ali[0][0]=='-' or ali[1][len(ali[1])-1]=='-')
    

        
def buildAlignment(sequences):
    la = QSolexaReverseAssemble()
    ra = QSolexaRightReverseAssemble()
    
    for d,r in sequences:
        if len(d)==0 or len(r)==0:
            continue
        la.seqA=d 
        la.seqB=r 
        ali=la()
        ali.direction='left'
        if not checkAlignOk(ali):
#            print >>sys.stderr,"-> bad : -------------------------"
#            print >>sys.stderr,ali
#            print >>sys.stderr,"----------------------------------"
            ra.seqA=d 
            ra.seqB=r
            ali=ra()
            ali.direction='right'
#            print >>sys.stderr,ali
#            print >>sys.stderr,"----------------------------------"
        yield ali
        
        
    
    
if __name__ == '__main__':
    optionParser = getOptionManager([addSolexaPairEndOptions],
                                    entryIterator=fastqSolexaIterator
                                    )
    
    (options, direct) = optionParser()
    
    if options.reverse is None:
        sequences=cutDirectReverse(direct)
    else:
        reverse = fastqSolexaIterator(options.reverse)
        sequences=seqPairs(direct,reverse)
    
    for ali in buildAlignment(sequences):
        consensus = buildConsensus(ali)
        print formatFastq(consensus)
        
        

