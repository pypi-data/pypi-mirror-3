"""
    Module providing high level functions to manage command line options.
"""
import logging
import sys

from logging import debug

from optparse import OptionParser

from obitools.utils import universalOpen
from obitools.utils import fileSize
from obitools.utils import universalTell
from obitools.utils import progressBar
from obitools.format.options import addInputFormatOption, addInOutputOption,\
    autoEntriesIterator
import time
    


def getOptionManager(optionDefinitions,entryIterator=None,progdoc=None):
    '''
    Build an option manager fonction. that is able to parse
    command line options of the script.
    
    @param optionDefinitions: list of function describing a set of 
                              options. Each function must allows as
                              unique parametter an instance of OptionParser.
    @type optionDefinitions:  list of functions.
    
    @param entryIterator:     an iterator generator function returning
                              entries from the data files. 
                              
    @type entryIterator:      an iterator generator function with only one
                              parametter of type file
    '''
    parser = OptionParser(progdoc)
    parser.add_option('--DEBUG',
                      action="store_true", dest="debug",
                      default=False,
                      help="Set logging in debug mode")

    parser.add_option('--no-psyco',
                      action="store_true", dest="noPsyco",
                      default=False,
                      help="Don't use psyco even if it installed")

    parser.add_option('--without-progress-bar',
                      action="store_false", dest="progressbar",
                      default=True,
                      help="desactivate progress bar")

    checkFormat=False
    for f in optionDefinitions:
        if f == addInputFormatOption or f == addInOutputOption:
            checkFormat=True 
        f(parser)
        
    def commandLineAnalyzer():
        options,files = parser.parse_args()
        if options.debug:
            logging.root.setLevel(logging.DEBUG)
            
        if checkFormat:
            ei=autoEntriesIterator(options)
        else:
            ei=entryIterator
        
        i = allEntryIterator(files,ei,with_progress=options.progressbar)
        return options,i
    
    return commandLineAnalyzer

_currentInputFileName=None
_currentFile = None
_currentFileSize = None

def currentInputFileName():
    return _currentInputFileName

def currentInputFile():
    return _currentFile

def currentFileSize():
    return _currentFileSize

def currentFileTell():
    return universalTell(_currentFile)

def fileWithProgressBar(file,step=100):
    try:
        size = currentFileSize()
    except:
        size = None
                
    def fileBar():
        pos=1
        progressBar(pos, size, True,currentInputFileName())
        for l in file:
            progressBar(currentFileTell,size,head=currentInputFileName())
            yield l 
        print >>sys.stderr,''    
    if size is None:
        return file
    else:
        f = fileBar()
        return f


def allEntryIterator(files,entryIterator,with_progress=False,histo_step=102):
    global _currentFile
    global _currentInputFileName
    global _currentFileSize
    if files :
        for f in files:
            _currentInputFileName=f
            f = universalOpen(f)
            _currentFile=f
            _currentFileSize=fileSize(_currentFile)
            debug(f)
            if with_progress:
                f=fileWithProgressBar(f,step=histo_step)
            if entryIterator is None:
                for line in f:
                    yield line
            else:
                for entry in entryIterator(f):
                    yield entry
    else:
        if entryIterator is None:
            for line in sys.stdin:
                yield line
        else:
            for entry in entryIterator(sys.stdin):
                yield entry
            
            