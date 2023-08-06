#!/usr/local/bin/python

'''
Created on 24 juin 2009

@author: coissac
'''

import re
from logging import root,DEBUG

from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption

def addTableOptions(optionManager):
    optionManager.add_option('-n','--na-string',
                             action="append", dest="NA",
                             metavar="<NOT AVAILABLE STRING>",
                             type="string",
                             default="NA",
                             help="String write in the table for not available value"
                            )
    optionManager.add_option('-o','--output-seq',
                             action="store_true", dest="sequence",
                             metavar="<NOT AVAILABLE STRING>",
                             default=False,
                             help="Add an extra column for sequence"
                            )
    optionManager.add_option('-d','--no-definition',
                             action="store_false", dest="definition",
                             metavar="<NOT AVAILABLE STRING>",
                             default=True,
                             help="Remove column for sequence definition"
                            )
    optionManager.add_option('-k','--omit-key',
                             action="append", dest="omit",
                             metavar="<KEY NAME>",
                             default=[],
                             help="Add key name to omit in the output tab"
                            )
    
    optionManager.add_option('-c','--common-key',
                             action="append", dest="omit",
                             metavar="<KEY NAME>",
                             default=[],
                             help="Add key name to omit in the output tab"
                            )
    


def headerCmp(h1,h2):
    if type(h1) is str and type(h2) is str:
        return cmp(h1, h2)
    if type(h1) is str and type(h2) is tuple:
        return cmp(h1, h2[0])
    if type(h1) is tuple and type(h2) is str:
        return cmp(h1[0], h2)
    if type(h1) is tuple and type(h2) is tuple:
        c = cmp(h1[0],h2[0])
        if c==0:
            c = cmp(h1[1],h2[1])
        return c
    raise AssertionError
            
    

    

if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

#    root.setLevel(DEBUG)

    optionParser = getOptionManager([addTableOptions,addInOutputOption])
    
    (options, entries) = optionParser()

    column = {}
    subcol = {}
    db = []
    for seq in entries: 
        db.append(seq)
        keys = seq.keys()      
        for k in keys:
            t=type(seq[k])
            if k in column:
                column[k].add(t)
            else:
                column[k]=set([t])
            if t is dict:
                if k not in subcol:
                    subcol[k]=set()
                subcol[k]|=set(seq[k].keys())
                
    headers = set()
    for c in column:
        if len(column[c])==1:
            column[c]=column[c].pop()
        else:
            column[c]=str
            
        if column[c] not in (str,int,float,dict,bool):
            column[c]=str

            
        if column[c] is not dict:
            headers.add(c)
        else:
            for sc in subcol[c]:
                headers.add((c,sc))
                
    omit = set(options.omit)
    headers=list(headers)
    headers.sort(headerCmp)
        
    print "id",
    if options.definition:
        print '\tdefinition',

    for k in headers:
        if type(k) is str:
            if k not in omit:
                print '\t',k,
        else:
            if k[0][0:7] not in omit:
                if k[0][0:7]=='merged_':
                    print '\t%s:%s' % (k[0][7:],str(k[1])),
                else:
                    print '\t%s:%s' % (k[0],str(k[1])),
            
    if options.sequence:
        print "\tsequence",
    print 
        
    
    for seq in db:
        print seq.id,
        
        if options.definition:
            print '\t',seq.definition,
            
        for k in headers:
            if type(k) is str:
                if k not in omit:
                    if k in seq:
                        print '\t',seq[k],
                    else:
                        print '\t',options.NA,
            else:
                if k[0] not in omit:
                    if k[0] in seq:
                        sk = seq[k[0]]
                    else:
                        sk={}
                    if k[1] in sk:
                        print '\t',sk[k[1]],
                    else:
                        if k[0][0:7]=='merged_':
                            print '\t',0,
                        else:
                            print '\t',options.NA,
        if options.sequence:
            print '\t',str(seq)
        else:
            print
    
            
        
            
