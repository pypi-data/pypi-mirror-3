# cython: profile=True

import re
from _fasta cimport *

_parseFastaTag=re.compile('([a-zA-Z]\w*) *= *([^;]+);')

cpdef _fastaJoinSeq(seqarray):
    return  ''.join([x.strip() for x in seqarray])


cpdef parseFastaDescription(str ds, object tagparser=_parseFastaTag):
    
    cdef dict info
    cdef str definition
    cdef str x
    cdef str y
    cdef object match,m
    
    info = {x:y.strip() for x,y in tagparser.findall(ds)}
#    l=[i for i in tagparser.finditer(ds)]
#    for m in l:
#        match=m
#        x,y = m.group(1,2)
#        info[x]=y.strip()
#     
#    print "\n\n\n",str(type(l[-1])),'\n\n\n'
#    s = slice(m.end())
#    definition = ds[s]   
    
    definition = tagparser.sub('',ds).strip()    

    return definition,info

cpdef fastaParser(seq,bioseqfactory,tagparser=_parseFastaTag,joinseq=_fastaJoinSeq):
    '''
    Parse a fasta record.
    
    @attention: internal purpuse function
    
    @param seq: a sequence object containing all lines corresponding
                to one fasta sequence
    @type seq: C{list} or C{tuple} of C{str}
    
    @param bioseqfactory: a callable object return a BioSequence
                          instance.
    @type bioseqfactory: a callable object
    
    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: a C{BioSequence} instance   
    '''
    cdef char *title
    cdef char *sequence
    cdef char* clean1
    cdef char* clean2
    
    title=seq
    title+=1
    sequence=seq
    
    while(sequence[0]!='\n'):
     sequence+=1 
    
    clean1=sequence-1
    while(clean1[0]==' ' or clean1[0]=='\t'):
        clean1[0]==0;
        clean1-=1
    
    sequence[0]=0
    
    sequence+=1
    clean1=sequence
    clean2=sequence
    
    while (clean1[0]!='\x00'):
        clean2[0]=clean1[0]
        clean1+=1
        if clean2[0]!=' ' and clean2[0]!='\n':
            clean2+=1
            
    clean2[0]=0
    seq=str(sequence)
    
    
    #seq = seq.split('\n')
    tit = str(title).split(None,1)
    id=tit[0]
    if len(tit) == 2:
        definition,info=parseFastaDescription(tit[1], tagparser)
    else:
        info= {}
        definition=None

    #seq=joinseq(seq[1:])
    return bioseqfactory(id, seq, definition,False,**info)
