from obitools.fasta import fastaIterator
from obitools.fastq import fastqSangerIterator
from obitools.seqdb.embl.parser import emblIterator
from obitools.seqdb.genbank.parser import genbankIterator
from itertools import chain
from obitools.utils import universalOpen

def autoSequenceIterator(file):
    lineiterator = universalOpen(file)
    first = lineiterator.next()
    if first[0]==">":
            reader=fastaIterator
    elif first[0]=='@':
        reader=fastqSangerIterator
    elif first[0:3]=='ID ':
        reader=emblIterator
    elif first[0:6]=='LOCUS ':
        reader=genbankIterator
    else:
        raise AssertionError,'file is not in fasta, fasta, embl, or genbank format'
    
    input = reader(chain([first],lineiterator))
    
    return input
