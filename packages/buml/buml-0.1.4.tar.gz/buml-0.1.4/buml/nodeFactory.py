#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
===========
nodeFactory
===========

This module is a part of *buml*.

:Author and Copyright:  Bud P. Bruegger
:License:               FreeBSD

This module provides the functionality to map syntactic constructs to Nodes.
"""

import re

SINGLE_LINE_TYPES = list('/!|*{')
#-- start for testing only -----------------
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# SINGLE_LINE_TYPES = list('/!|*>')
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

LEGAL_EL_NAME = re.compile('^[a-zA-Z:_%][a-zA-Z0-9-:_]*$')

#----------------------------------------
class NodeFactoryError(Exception):
    pass
#----------------------------------------

class NodeFactory(object):

    def __init__(self, nodesModule=None):
        if nodesModule:
            nm = nodesModule
        else:
            import baseWriterNodes
            nm = baseWriterNodes
        self.nodesModule = nm

    def isSingleLineNode(self, lineTypeChar):
        return lineTypeChar in SINGLE_LINE_TYPES
    
    def isValidElementName(self, name):
        return LEGAL_EL_NAME.match(name)

    def mkRootNode(self):
        return self.nodesModule.Node()
     
    def mkTextNode(self, txt, enableInlineParsing=True):
        return self.nodesModule.Text(txt)

    def mkSingleLineNode(self, lineStr):
        lineStr = lineStr.lstrip() #better slow than sorry
        typeChar = lineStr[0]
        specStr = lineStr[1:].strip()
        if typeChar == '/':
            return self.nodesModule.BumlComment(txt=specStr)
        if typeChar == '!':
            return self.nodesModule.XmlComment(txt=specStr)
        if typeChar == '|':
            return self.nodesModule.DocTypeDecl(txt=specStr)
        if typeChar == '*':
            return self.nodesModule.Macro(txt=specStr)
        if typeChar == '{':
            return self.nodesModule.Template(tag=specStr[0], txt=specStr[1:].strip())
        #-- start for testing only -----------------
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        #if typeChar == '>':
        #    return self.nodesModule.XmlComment(txt=specStr)
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        raise(NodeFactoryError('unexpeted single line node type'))
    
    def mkElementNode(self, tagName, attDict=None):
        attDict = attDict or {}
        char = tagName[0]
        if char == '?':
            return self.nodesModule.ProcessingInstruction(tag=tagName[1:].strip(), \
                                                          atts=attDict)
        if char == '[':  #no strip to preserve whitespace
            return self.nodesModule.CDATA(tag='', txt=tagName[1:])
        if self.isValidElementName(tagName):
            return self.nodesModule.Element(tag=tagName, atts=attDict)
        else:
            raise(NodeFactoryError('unexpeted element name "%s"' % tagName))
            
    
