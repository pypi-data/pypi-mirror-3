"""
fasta module provides functions to read and write sequences in fasta format.


"""

#from obitools.format.genericparser import fastGenericEntryIteratorGenerator
from obitools.format.genericparser import genericEntryIteratorGenerator
from obitools import bioSeqGenerator,BioSequence,AASequence,NucSequence
from obitools import _default_raw_parser

#from obitools.alignment import alignmentReader
#from obitools.utils import universalOpen

import re
from obitools.ecopcr.options import loadTaxonomyDatabase
from obitools.format import SequenceFileIterator

#from _fasta import parseFastaDescription,fastaParser
#from _fasta import _fastaJoinSeq
#from _fasta import _parseFastaTag


#fastaEntryIterator=fastGenericEntryIteratorGenerator(startEntry='>')
fastaEntryIterator=genericEntryIteratorGenerator(startEntry='>')
rawFastaEntryIterator=genericEntryIteratorGenerator(startEntry='\s*>')

def _fastaJoinSeq(seqarray):
    return  ''.join([x.strip() for x in seqarray])


def parseFastaDescription(ds,tagparser):
    
    m = tagparser.search(' '+ds)
    if m is not None:
        info=m.group(0)
        definition = ds[m.end(0):].strip()
    else:
        info=None
        definition=ds
 
    return definition,info

def fastaParser(seq,bioseqfactory,tagparser,rawparser,joinseq=_fastaJoinSeq):
    '''
    Parse a fasta record.
    
    @attention: internal purpose function
    
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
    seq = seq.split('\n')
    title = seq[0].strip()[1:].split(None,1)
    id=title[0]
    if len(title) == 2:
        definition,info=parseFastaDescription(title[1], tagparser)
    else:
        info= None
        definition=None

    seq=joinseq(seq[1:])
    return bioseqfactory(id, seq, definition,info,rawparser)


def fastaNucParser(seq,tagparser=_default_raw_parser,joinseq=_fastaJoinSeq):
    return fastaParser(seq,NucSequence,tagparser=tagparser,joinseq=_fastaJoinSeq)

def fastaAAParser(seq,tagparser=_default_raw_parser,joinseq=_fastaJoinSeq):
    return fastaParser(seq,AASequence,tagparser=tagparser,joinseq=_fastaJoinSeq)

def fastaIterator(file,bioseqfactory=bioSeqGenerator,
                  tagparser=_default_raw_parser,
                  joinseq=_fastaJoinSeq):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be BioSequence
    instances

    @param file: a line iterator containing fasta data or a filename
    @type file:  an iterable object or str
    @param bioseqfactory: a callable object return a BioSequence
                          instance.
    @type bioseqfactory: a callable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{BioSequence} instance
 
    @see: L{fastaNucIterator}
    @see: L{fastaAAIterator}
    
    >>> from obitools.format.sequence.fasta import fastaIterator
    >>> f = fastaIterator('monfichier')
    >>> s = f.next()
    >>> print s
    gctagctagcatgctagcatgcta
    >>>
    '''
    rawparser=tagparser
    allparser = tagparser % '[a-zA-Z][a-zA-Z0-9_]*'
    tagparser = re.compile('( *%s)+' % allparser)

    for entry in fastaEntryIterator(file):
        yield fastaParser(entry,bioseqfactory,tagparser,rawparser,joinseq)
        
def rawFastaIterator(file,bioseqfactory=bioSeqGenerator,
                     tagparser=_default_raw_parser,
                     joinseq=_fastaJoinSeq):

    rawparser=tagparser
    allparser = tagparser % '[a-zA-Z][a-zA-Z0-9_]*'
    tagparser = re.compile('( *%s)+' % allparser)

    for entry in rawFastaEntryIterator(file):
        entry=entry.strip()
        yield fastaParser(entry,bioseqfactory,tagparser,rawparser,joinseq)

def fastaNucIterator(file,tagparser=_default_raw_parser):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{NucBioSequence} instance
    @rtype: a generator object
    
    @see: L{fastaIterator}
    @see: L{fastaAAIterator}
    '''
    return fastaIterator(file, NucSequence,tagparser)

def fastaAAIterator(file,tagparser=_default_raw_parser):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be AASequence
    instances
    
    @param file: a line iterator containing fasta data
    @type file: an iterable object
    
    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{AABioSequence} instance

    @see: L{fastaIterator}
    @see: L{fastaNucIterator}
    '''
    return fastaIterator(file, AASequence,tagparser)

def formatFasta(data,gbmode=False,upper=False,restrict=None):
    '''
    Convert a seqence or a set of sequences in a
    string following the fasta format
    
    @param data: sequence or a set of sequences
    @type data: BioSequence instance or an iterable object 
                on BioSequence instances
                
    @param gbmode: if set to C{True} identifier part of the title
                   line follows recommendation from nbci to allow
                   sequence indexing with the blast formatdb command.
    @type gbmode: bool
                
    @param restrict: a set of key name that will be print in the formated
                     output. If restrict is set to C{None} (default) then
                     all keys are formated.
    @type restrict: any iterable value or None
    
    @return: a fasta formated string
    @rtype: str
    '''
    if isinstance(data, BioSequence):
        data = [data]

    if restrict is not None and not isinstance(restrict, set):
        restrict = set(restrict)    

    rep = []
    for sequence in data:
        seq = str(sequence)
        if sequence.definition is None:
            definition=''
        else:
            definition=sequence.definition
        if upper:
            frgseq = '\n'.join([seq[x:x+60].upper() for x in xrange(0,len(seq),60)])
        else:
            frgseq = '\n'.join([seq[x:x+60] for x in xrange(0,len(seq),60)])
        info='; '.join(['%s=%s' % x 
                        for x in sequence.rawiteritems()
                        if restrict is None or x[0] in restrict])
        if info:
            info=info+';'
        if sequence._rawinfo is not None and sequence._rawinfo:
            info+=" " + sequence._rawinfo.strip()
            
        id = sequence.id
        if gbmode:
            if 'gi' in sequence:
                id = "gi|%s|%s" % (sequence['gi'],id)
            else:
                id = "lcl|%s|" % (id)
        title='>%s %s %s' %(id,info,definition)
        rep.append("%s\n%s" % (title,frgseq))
    return '\n'.join(rep)

def formatSAPFastaGenerator(options):
    loadTaxonomyDatabase(options)
    
    taxonomy=None
    if options.taxonomy is not None:
        taxonomy=options.taxonomy
    
    assert taxonomy is not None,"SAP formating require indication of a taxonomy database"

    ranks = ('superkingdom', 'kingdom', 'subkingdom', 'superphylum', 
             'phylum', 'subphylum', 'superclass', 'class', 'subclass', 
             'infraclass', 'superorder', 'order', 'suborder', 'infraorder', 
             'parvorder', 'superfamily', 'family', 'subfamily', 'supertribe', 'tribe', 
             'subtribe', 'supergenus', 'genus', 'subgenus', 'species group', 
             'species subgroup', 'species', 'subspecies')
    
    trank=set(taxonomy._ranks)
    ranks = [taxonomy._ranks.index(x) for x in ranks if x in trank]
    
    strict= options.strictsap
    
    def formatSAPFasta(data,gbmode=False,upper=False,restrict=None):
        '''
        Convert a seqence or a set of sequences in a
        string following the fasta format as recommended for the SAP
        software 
        
        http://ib.berkeley.edu/labs/slatkin/munch/StatisticalAssignmentPackage.html
        
        @param data: sequence or a set of sequences
        @type data: BioSequence instance or an iterable object 
                    on BioSequence instances
                    
        @param gbmode: if set to C{True} identifier part of the title
                       line follows recommendation from nbci to allow
                       sequence indexing with the blast formatdb command.
        @type gbmode: bool
                    
        @param restrict: a set of key name that will be print in the formated
                         output. If restrict is set to C{None} (default) then
                         all keys are formated.
        @type restrict: any iterable value or None
        
        @return: a fasta formated string
        @rtype: str
        '''
        if isinstance(data, BioSequence):
            data = [data]
    
        if restrict is not None and not isinstance(restrict, set):
            restrict = set(restrict)    
    
        rep = []
        for sequence in data:
            seq = str(sequence)

            if upper:
                frgseq = '\n'.join([seq[x:x+60].upper() for x in xrange(0,len(seq),60)])
            else:
                frgseq = '\n'.join([seq[x:x+60] for x in xrange(0,len(seq),60)])
                        
            try:    
                taxid = sequence["taxid"]
            except KeyError:
                if strict:
                    raise AssertionError('All sequence must have a taxid')
                else:
                    continue
                
            definition=' ;'
            
            for r in ranks:
                taxon = taxonomy.getTaxonAtRank(taxid,r)
                if taxon is not None:
                    definition+=' %s: %s,' % (taxonomy._ranks[r],taxonomy.getPreferedName(taxon))
                    
            definition='%s ; %s' % (definition[0:-1],taxonomy.getPreferedName(taxid))
            
            id = sequence.id
            if gbmode:
                if 'gi' in sequence:
                    id = "gi|%s|%s" % (sequence['gi'],id)
                else:
                    id = "lcl|%s|" % (id)
            title='>%s%s' %(id,definition)
            rep.append("%s\n%s" % (title,frgseq))
        return '\n'.join(rep)

    return formatSAPFasta

class FastaIterator(SequenceFileIterator):
    
    
    entryIterator = genericEntryIteratorGenerator(startEntry='>')
    classmethod(entryIterator)
    
    def __init__(self,inputfile,bioseqfactory=bioSeqGenerator,
                      tagparser=_default_raw_parser,
                      joinseq=_fastaJoinSeq):
        
        SequenceFileIterator.__init__(self, inputfile, bioseqfactory)

        self.__file = FastaIterator.entryIterator(self._inputfile)
        
        self._tagparser = tagparser
        self._joinseq   = joinseq

    def get_tagparser(self):
        return self.__tagparser


    def set_tagparser(self, value):
        self._rawparser = value
        allparser = value % '[a-zA-Z][a-zA-Z0-9_]*'
        self.__tagparser = re.compile('( *%s)+' % allparser)

    def _parseFastaDescription(self,ds):
        
        m = self._tagparser.search(' '+ds)
        if m is not None:
            info=m.group(0)
            definition = ds[m.end(0):].strip()
        else:
            info=None
            definition=ds
     
        return definition,info


    def _parser(self):
        '''
        Parse a fasta record.
        
        @attention: internal purpose function
                
        @return: a C{BioSequence} instance   
        '''
        seq = self._seq.split('\n')
        title = seq[0].strip()[1:].split(None,1)
        id=title[0]
        if len(title) == 2:
            definition,info=self._parseFastaDescription(title[1])
        else:
            info= None
            definition=None
    
        seq=self._joinseq(seq[1:])
        
        return self._bioseqfactory(id, seq, definition,info,self._rawparser)
    
    _tagparser = property(get_tagparser, set_tagparser, None, "_tagparser's docstring")
