#!/usr/local/bin/python
"""\
-------------------------------------------------------
 fastalength.py
-------------------------------------------------------

fastaLength.py [-h|--help] <fastafile>"

    add length data on all sequences in the fasta file.

-------------------------------------------------------
-h    --help                       : print this help
-------------------------------------------------------
"""

from obitools.fasta import fastaIterator,formatFasta
from obitools.options import getOptionManager
from obitools.utils import deprecatedScript
    

if __name__=='__main__':
    
    deprecatedScript('obiannotate')
    
    optionParser = getOptionManager([],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()
    
    for seq in entries:
            seq['seqLength']=len(seq)
            print formatFasta(seq)
            
            