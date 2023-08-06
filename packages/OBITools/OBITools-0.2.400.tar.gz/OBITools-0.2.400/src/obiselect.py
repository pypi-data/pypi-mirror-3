#!/usr/local/bin/python
"""
:py:mod:`obiselect` : Select and print sequences identified by a list of IDs 
============================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obiselect` command allows to select a set of sequences identified by a list of IDs.

Note that the supplied identifiers are not required to correspond to any existing sequence identifier.
If an ID is not found, no warning will be produced.

Option -v allows to invert the selection and thus select sequences whose IDs are not in the list.

Example:

.. code-block:: bash

   > obiselect --identifier IDs.list seq.fasta > selectedSeq.fasta


"""
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager

def addSelectOptions(optionManager):
    
    optionManager.add_option('-i','--identifier',
                             action="store", dest="identifier",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file containing sample sequences to select on "
                                  "on the base of their identifier")

    optionManager.add_option('-v',
                             action="store_true", dest="invert",
                             default=False,
                             help="invert selection")




if __name__ == '__main__':
    optionParser = getOptionManager([addSelectOptions,addInOutputOption], progdoc=__doc__)
    
    (options, entries) = optionParser()
    
    idset=set(x.strip() for x in  open(options.identifier))
    writer = sequenceWriterGenerator(options)
    
    def invert(x):
        if options.invert:
            return not x
        else:
            return x
    
    for seq in entries:
        if invert(seq.id in idset):
            writer(seq)
        
