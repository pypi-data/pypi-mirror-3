#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
============
inlineParser
============

This module is a part of *buml*.

:Author and Copyright:  Bud P. Bruegger
:License:               FreeBSD

This is the standard inline parser that comes with buml.

The inlineFactory provides functions that map a parsed string to a node
(node-level function) or text (text-level )
"""
from mappingSpec import MappingSpec, MappingSpecItem
from utilities import addrNameFromString
from inlineParser import parse


class InlineMapper(object):

    def __init__(self, nodeFactoryInstance=None):
        if nodeFactoryInstance:
            nf = nodeFactoryInstance           
        else:
            import nodeFactory
            nf = nodeFactory.NodeFactory()
        self.nodeFactory = nf

    def textHandler(self, txt):
        return [self.nodeFactory.mkTextNode(txt)]

    def _singleElHandler(self, txt, elTag, elAtts=None, recurse=True):
        atts = elAtts or {}
        el = self.nodeFactory.mkElementNode(elTag, atts)
        if recurse:
            children = parse(txt, self.mappingSpec()) #recursive parsing
        else:
            children = [self.nodeFactory.mkTextNode(txt)]
        el.setChildren(children)
        return [el]

    def emHandler(self, txt):
        return self._singleElHandler(txt, 'em')

    def strongHandler(self, txt):
        return self._singleElHandler(txt, 'strong')

    def linkHandler(self, txt):
        addr, name = addrNameFromString(txt)
        attD = {'href': addr}
        return self._singleElHandler(name, 'a', elAtts=attD)

    def replaceHandler(self, txt):
        return self._singleElHandler(txt, 'replace', recurse=False)
        
    def mappingSpec(self):
        "returns the mappingSpec"
        m = MappingSpec()
        #necessary Null Mapper for Text without matches:
        m.append(MappingSpecItem('', '', self.textHandler))
        m.append(MappingSpecItem('*', '*', self.emHandler))
        m.append(MappingSpecItem('**', '**', self.strongHandler))
        m.append(MappingSpecItem('[[', ']]', self.linkHandler))
        m.append(MappingSpecItem('::', '::', self.replaceHandler, 
                                 singleWord=True))
        return m
    


