'''
Created on 29 aout 2009

@author: coissac
'''

from obitools import BioSequence
from obitools import _default_raw_parser
from obitools.format.genericparser import genericEntryIteratorGenerator
from obitools import bioSeqGenerator,AASequence,NucSequence
from obitools.fasta import parseFastaDescription
from _fastq import fastqQualitySangerDecoder,fastqQualitySolexaDecoder
from _fastq import qualityToSangerError,qualityToSolexaError
from _fastq import errorToSangerFastQStr
from _fastq import formatFastq
from _fastq import fastqParserGenetator
from obitools.utils import universalOpen

import re 

fastqEntryIterator=genericEntryIteratorGenerator(startEntry='^@',endEntry="^\+",strip=True,join=False)

#def fastqParserGenetator(fastqvariant='sanger',bioseqfactory=NucSequence,tagparser=_parseFastaTag):
#    
#    qualityDecoder,errorDecoder = {'sanger'   : (fastqQualitySangerDecoder,qualityToSangerError),
#                                   'solexa'   : (fastqQualitySolexaDecoder,qualityToSolexaError),
#                                   'illumina' : (fastqQualitySolexaDecoder,qualityToSangerError)}[fastqvariant]
#
#    def fastqParser(seq):
#        '''
#        Parse a fasta record.
#        
#        @attention: internal purpose function
#        
#        @param seq: a sequence object containing all lines corresponding
#                    to one fasta sequence
#        @type seq: C{list} or C{tuple} of C{str}
#        
#        @param bioseqfactory: a callable object return a BioSequence
#                              instance.
#        @type bioseqfactory: a callable object
#        
#        @param tagparser: a compiled regular expression usable
#                          to identify key, value couples from 
#                          title line.
#        @type tagparser: regex instance
#        
#        @return: a C{BioSequence} instance   
#        '''
#        
#        title = seq[0][1:].split(None,1)
#        id=title[0]
#        if len(title) == 2:
#            definition,info=parseFastaDescription(title[1], tagparser)
#        else:
#            info= {}
#            definition=None
#        
#        quality=errorDecoder(qualityDecoder(seq[3]))
#    
#        seq=seq[1]
#        
#        seq = bioseqfactory(id, seq, definition,False,**info)
#        seq.quality = quality
#        
#        return seq
#    
#    return fastqParser


def fastqIterator(file,fastqvariant='sanger',bioseqfactory=NucSequence,tagparser=_default_raw_parser):
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

    '''
    fastqParser=fastqParserGenetator(fastqvariant, bioseqfactory, tagparser)
    file = universalOpen(file)
    for entry in fastqEntryIterator(file):
        title=entry[0]
        seq="".join(entry[1:-1])
        quality=''
        lenseq=len(seq)
        while (len(quality) < lenseq):
            quality+=file.next().strip()
            
        yield fastqParser([title,seq,'+',quality])

def fastqSangerIterator(file,tagparser=_default_raw_parser):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastqIterator}
    @see: L{fastqAAIterator}
    '''
    return fastqIterator(file,'sanger',NucSequence,tagparser)

def fastqSolexaIterator(file,tagparser=_default_raw_parser):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastqIterator}
    @see: L{fastqAAIterator}
    '''
    return fastqIterator(file,'solexa',NucSequence,tagparser)

def fastqIlluminaIterator(file,tagparser=_default_raw_parser):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastqIterator}
    @see: L{fastqAAIterator}
    '''
    return fastqIterator(file,'illumina',NucSequence,tagparser)

def fastqAAIterator(file,tagparser=_default_raw_parser):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be AASequence
    instances
    
    @param file: a line iterator containing fasta data
    @type file: an iterable object
    
    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{AABioSequence} instance

    @see: L{fastqIterator}
    @see: L{fastqNucIterator}
    '''
    return fastqIterator(file,'sanger',AASequence,tagparser)


