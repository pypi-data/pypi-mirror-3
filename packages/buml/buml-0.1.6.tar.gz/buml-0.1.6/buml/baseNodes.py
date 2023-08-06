#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
=========
BaseNodes
=========

This module is a part of *buml*.

:Author and Copyright:  Bud P. Bruegger
:License:               FreeBSD

This module provides basic nodes of different types to build a parse tree.  It
includes some methods to navigate through trees and inspect elements.  

It is agnostic of any Writer capability, i.e., knowledge of how to render nodes
in different output formats (xml, html, other).

Writers and Transformers are meant to subclass the classes of this module to
add writer/transformer-specific methods.  
"""


import pprint

#import re

#== Utility Classes ==================================================

class MultiDict(object):
    def __init__(self, _dict= None):
        _dict = _dict or {}
        self._dict = {}
        for k, v in _dict.items():
            self.insert(k, v)

    def __nonzero__(self):
        return bool(self._dict)

    def asDict(self):
        return self._dict
    
    def __eq__(self, other):
        return self.asDict() == other.asDict()

    def insert(self, key, val):
        if key in self._dict:
            self._dict[key].append(val)
        else:
            self._dict[key] = [val]

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self.insert(key, value)

    def items(self):
        return self._dict.items()

    def update(self, mDict):
        for k, vList in mDict.items():
            for v in vList:
                self.insert(k, v)

    def clone(self):
        "returns a different instance with equal content"
        md = MultiDict()
        md._dict = self._dict.copy()
        return md

    def contains(self, _dict):
        "True if all dict items are included"
        for key, val in _dict.items():
            if not key in self._dict or not val in self._dict[key]:
                return False
        return True

  
#== Node Classes ==================================================

class Node(object):
    def __init__(self, txt=''):
        self.children = []
        self.parent = None
        self.txt = txt

    def __repr__(self):
        if not self.parent and self.__class__.__name__ == 'Node':
            detailStr = "I'm the root"
        elif self.txt:
            if len(self.txt) < 9: 
                detailStr = '"%s"' % self.txt
            else:
                detailStr = '"%s.."' % self.txt[:8]
        else:
            detailStr = ''
        if detailStr: 
            detailStr = ": %s" % detailStr
        return "<%s instance%s>" % (self.__class__.__name__, detailStr)

    def addChild(self, child):
        self.children.append(child)
        child.parent = self

    def delChild(self, child):
        child.parent = None
        self.children.remove(child)

    def _updateParentInChildren(self):
        "updates the parent in all children to self"
        for child in self.children:
            child.parent = self

    def setChildren(self, childL):
        "sets children to given list of children"
        self.children = childL
        self._updateParentInChildren()

    def replaceWith(self, substNodeOrList):
        "replaces self with substNode or a list of Nodes"
        # if node has children, they are attached at the first
        # node in the list
        childNdx = self.parent.children.index(self)
        if isinstance(substNodeOrList, list):
            nodeL = substNodeOrList
        else:
            nodeL = [substNodeOrList]
        for node in nodeL:
            node.parent = self.parent
        if self.children:
            nodeL[0].children = self.children
            nodeL[0]._updateParentInChildren()
        self.parent.children[childNdx:childNdx+1] = nodeL


    def __getitem__(self, key):
        return self.children[key]

    def asNestedList(self):
        if self.children:
            childReps = [c.asNestedList() for c in self.children]
            return [self, childReps]
        else:
            #return [self]
            return self

    def pprint(self, indent=2):
        pprint.pprint(self.asNestedList(), indent=indent)

    def _isEligibleEl(self, tagVals, attVals, elClassName):
        return False 
        #baseNode never shows up
        #specialize in subclass

    def findAllEls(self, tagVals=None, attVals=None, elClassName='Element'):
        """returns a list of all ancester Elements
           optionally of given tag or attribute values
        """
        tagVals = tagVals or []
        attVals = attVals or {}
        l = []
        if self._isEligibleEl(tagVals, attVals, elClassName):
            l.append(self)
        for child in self.children:
            l.extend(child.findAllEls(tagVals, attVals))
        return l

    def _isEligibleNode(self, nodeType, selectFunct):
        if nodeType and not self.__class__.__name__ == nodeType:
            return False
        if selectFunct and not selectFunct(self):
            return False
        return True

    def findAllNodes(self, nodeType='', selectFunct=None):
        """returns a list of all ancester Nodes
           of a given type
           selectFunct takes a node as input and returns
           True if it needs to be included, and False otherwise
        """
        l = []
        if self._isEligibleNode(nodeType, selectFunct):
            l.append(self)
        for child in self.children:
            l.extend(child.findAllNodes(nodeType, selectFunct))
        return l


    def lastNonTextNode(self):
        "decends in a line of single decendents (children[0]) and returns the last non-Text-Node"
        lastN = self
        while lastN.children and not isinstance(lastN.children[0], Text):
            lastN = lastN.children[0]
        return lastN

#---------------------------------------------------------------------
class GenEl(Node):
    "a generic element (not xml-elemnt) that is not used by itself"

    def __init__(self, tag='', txt='', atts=None):
        "att is dict or MultiDict"
        Node.__init__(self, txt)
        if atts:
           if atts.__class__.__name__ == 'dict':
               myAtts = MultiDict(atts)
           else:
               myAtts = atts.clone()
        else:
           myAtts = MultiDict()
        self.tag = tag
        self.atts = myAtts

    def attDict(self):
        return self.atts.asDict()

    def addAttr(self, key, val):
        self.atts[key] = val

    def __repr__(self):
        if self.atts.asDict():
            detailStr = ': %s' % self.attDict()
        else: 
            detailStr = ''
        l = []
        classStr = self.__class__.__name__.split('.')[-1]
        if self.tag: l.append(self.tag)
        l.append(classStr)
        startStr = ' '.join(l)
        return '<%s%s>' % (startStr, detailStr)

    def _isEligibleEl(self, tagVals, attVals, elClassName):
        if self.__class__.__name__ != elClassName:
            return False
        if tagVals and not self.tag in tagVals:
            return False
        if attVals and not self.atts.contains(attVals):
            return False
        return True

#---------------------------------------------------------------------
class Text(Node): 
    pass


#-- Utility Functions ----------------------------

def linkNodes(listOfDecendents):
    "links all elements in parent child relationship"
    nodesRev = listOfDecendents[::-1]
    parent = nodesRev.pop()
    #print "!!! linkNodes: starting with %s" % parent
    while nodesRev:
        el = nodesRev.pop()
        #print "!!! linkNodes: adding %s to %s" % (el, parent)
        parent.addChild(el)
        parent = el
