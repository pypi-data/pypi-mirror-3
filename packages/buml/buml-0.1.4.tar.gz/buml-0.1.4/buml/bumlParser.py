#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
==========
bumlParser
==========

This module is a part of *buml*.

:Author and Copyright:  Bud P. Bruegger
:License:               FreeBSD

The buml parser takes a file in buml syntax and converts it in a tree of nodes
that is represented by the root node that the parser returns.  

The module that defines the node classes needs to be explicitly passed to the
parser function.  Usually, this module is a specialization of baseNodes. While
baseNodes provides the minimal functionality needed by the buml parser but
lacks the functionality of writers (which produce text (html, xml, ..) output
from a parse tree or transformer (which manipulates parse trees).  
"""
 

#  buml -- Bud's markup language
#  -----------------------------
#
#  Inspired by Sphaml (shpaml.webfactional.com) and 
#  Compact XML
#  http://packages.python.org/compactxml/
#
#  Limitations:
#  * '.' in tag name not possible, difficult to fix
#  
#  Every line is ether an element node or a text node.
#  
#  generic element names:          start with any character but  " & > . # @
#                                  ommission of tag name defaults to "div"
#  multiple decending elements:    separated by >
#  multiple same-level elements:   separated by &
#  classAttributes:                start with a .
#  idAttributes:                   start with a #
#  otherAttributes:                start with @ have an att value after =
#                                  multi-word values must be enclosed in '
#                                  omission of = and value defaults to
#                                  =True
#  single line text:               starts with "
#  multi line text:                starts with """
#
# -- the above markup is "built-in" and hard to modify
#
# -- the markup below is and assignment made by nodeFactory and is easy to modify
#                                  (eventually, this may become pluggable)
#
#  comments:                       starts with / on their own lines (also /* //)
#  xmlComments:                    start with !
#  templatingNodes:                start with { and require a second character
#                                  that indicates type: {{ or {%
#                                  (see e.g., http://jinja.pocoo.org/)
#  processingInstr:                start with ?
#  docTypeDecl:                    starts with |
#  CDATA sections:                 only a [ on a line by itself with text content
#
#  ----- not done yet -----
#  lineContinuations: start with \
#
#
#===============================================================
#  Notes on possible Evolution:
#  -------------------
#
#  * need to check for unexpected indent:  
#    - increasing indent steps at least by 2 chars
#    - decreasing lines use previously established indents
#  
#  * the parser should have an argument to pass in an inline parser that
#  processes all text.  As a result, it returns a list of nodes that can be
#  inserted in the tree.  An optional attribute (class is easy to write) may
#  indicate where to apply the inline parser.  
#  NO: THIS IS BETTER DONE BY A TRANSFORMER
#  
#  * idea for inline syntax: ..this is <<el1.class1@att=hi>el2#id1 |
#  http://cnn.com, tool tip | anchor text>> ..inline goes on Very easy to
#  parse: no nesting, simple splits do most of the job, rest already written
#  
#  A sorthand for often used things:  *italic* **bold**  (like in rst).  The
#  parser could have an argument to specify a mapping dictionary that mars
#  the markup ('*', '**', '|') to an element
#  
#  * a writer to ElementTree would interface to other tools
#  
#  * a reader from xml would include (documents or snipplets from other worlds)
#  
#  * maybe maybe a writer that returns an ReST (or Sphinx) parse tree???  But
#  how do I use this?
#  
#  * Sphinx integration:  Embed pages written in buml:
#    - Makefile addition
#    - use role raw
#    - convert buml nodes into ReST nodes ;-)  <== the winner idea
#    - how to use references and index entries??
#  
#  DONE
#  * Use % to indicate Django/Jinja nodes (e.g.,  {% extends "base.html" %},
#    as in http://shpaml.webfactional.com/long_example)
#
#===============================================================

import re
from baseNodes import MultiDict, linkNodes
from utilities import warning, findPatternPos, reQuote
#from utilities import warning, my_import

#== Classes ==================================================

class ParsingError(Exception):
    pass

class UnexpectedError(Exception):
    pass

class ConfigurationError(Exception):
    pass

#== Configuration Section ==================================================
# use configuration functions "config*" and "set*" to change these settings!

#== Utilities =======================================

def eliminateTabsSingleLine(lineStr):
    rest = lineStr.lstrip()
    indentStr = lineStr[:(len(lineStr) - len(rest))]
    if '\t' in indentStr:
        warning("Tab(s) found in ident string: %s" % lineStr)
    indentBlanks = indentStr.replace('\t', '    ')
    return indentBlanks + rest

def eliminateTabs(lines):
    return [eliminateTabsSingleLine(l) for l in lines]

def indent(lineStr):
    return len(lineStr) - len(lineStr.lstrip())

#def findSepPos(str):
#    "returns pos of first separator or -1"
#    match = TAG_PART_SEPARATORS.search(str)
#    if match:
#        return match.span()[0]
#    else:
#        return -1

def isEmpty(someStr):
    return not bool(someStr.strip())

def allLinesEmpty(lines):
    l = [l for l in lines if l.strip()]
    return not bool(l)

#-- parser stuff -------------------------------

def parseMultiLineTxt(txtFirstLine, txtStartPos, otherLines):
    """first line is already without indent, otherLines are raw

       pre: no mixed content
       pre: no empty lines
    """
    linesWOindent = [l[txtStartPos:] for l in otherLines]
    strippedLines = [txtFirstLine]
    strippedLines.extend(linesWOindent)
    return '\n'.join(strippedLines)

def subLineRange(lines):
    """selects the first line and all consecutive lines with
       a lesser indent (all markup corresponding to one node)
       returns selected lines and all non-selected ones as restLines

       note: skips over empty lines
    """
    lenlines = len(lines)
    if len(lines) == 1:
        return (lines, [])
    else:
        firstLineIndent = indent(lines[0])
        ndx = 1
        while ndx < lenlines and ((indent(lines[ndx]) > firstLineIndent) or isEmpty(lines[ndx])):
            ndx += 1
    return (lines[:ndx], lines[ndx:])

def subRanges(lines):
    "gets a list of all ranges at same indent level from lines"
    if len(lines)>0:
        l = []
        lineRange, restLines = subLineRange(lines)
        l.append(lineRange)
        if restLines:
            l.extend(subRanges(restLines))
        return l
    else:
        return []

#== Parser =======================================
class Parser(object):

    def _sepCharPattern(self):
        "returns re pattern for separator characters"
        sepCharStr = self._ID_CHR + self._CLS_CHR + self._ATT_CHR
        sepCharStr = reQuote(sepCharStr)
        pattern = '[%s]' % sepCharStr
        return re.compile(pattern)

    def __init__(self, nodeFactoryInstance=None):
        #module = my_import(nodeFactoryModuleName)
        if nodeFactoryInstance:
            nf = nodeFactoryInstance
        else:
            import nodeFactory
            nf = nodeFactory.NodeFactory()
        self.nodeFactory = nf
        self._TXT_CHR = '"'
        self._SAME_LEV_SEP = '&'  #a string
        self._DECENDING_SEP = '>' #a string
        self._CLS_CHR = '.'
        self._ID_CHR = '#'
        self._ATT_CHR = '@'
        self._EQ_CHR = '='
        self._ATT_QUOTE_CHR = "'"
        #-- update if s.th. changes
        self.TAG_PART_SEPARATORS = self._sepCharPattern()

    def updateAfterReConfig(self):
        """
        reconfigure after changing one or more special characters
        """
        self.TAG_PART_SEPARATORS = self._sepCharPattern()

    def _textParse(self, rawTxtPart, doubleQuotePos):
        "parses text after first double quote"
        if rawTxtPart[:2] == (2 * self._TXT_CHR): #a multi line txt
            isMultiLine = True
            txtPart = rawTxtPart[2:]
            startPos = doubleQuotePos + 3
        else:
            isMultiLine = False
            txtPart = rawTxtPart
            startPos = doubleQuotePos + 1
        return (txtPart, isMultiLine, startPos)

    def _tagTextSplit(self, lineStr):
        """splits tag part from text part
           operates on a full line that includes the indent
    
           returns: (tagSpec, text, isMultiLineTxt, txtStartPos)
        """
        pos = lineStr.find(self._TXT_CHR)
        if pos == -1:  
            return (lineStr.strip(), '', False, pos)
        tagPart = lineStr[:pos].strip()
        txtPart, isMultiLine, startPos = self._textParse(lineStr[pos+1:], pos)
        return (tagPart, txtPart, isMultiLine, startPos)

    def _tagSameLevelSplit(self, tagsStr):
        """same-level tags are separated by &"""
        l = tagsStr.split(self._SAME_LEV_SEP)
        return [i.strip() for i in l]

    def _tagDecendingSplit(self, tagsStr):
        """decending tags are separated by >"""
        l = tagsStr.split(self._DECENDING_SEP)
        return [i.strip() for i in l]
    
    def _parseGenAttr(self, attDef):
        "parses a general attribute"
        l = attDef.split(self._EQ_CHR)
        key = l[0]
        val = l[1] if len(l) == 2 else 'True'
        if val[0] == self._ATT_QUOTE_CHR:
            val = val[1:-1]
        return (key, val)
    
    def _tagAttrSplit(self, attsStr):
        """splits off the first attribute
           after tagName has already been removed
           pre: attsStr not empty
        """
        sepChr = attsStr[0]
        attsStr = attsStr[1:]
        nextSepPos = findPatternPos(attsStr, self.TAG_PART_SEPARATORS)
        #taking care of single-quoted att val
        eqPos = attsStr.find(self._EQ_CHR + self._ATT_QUOTE_CHR) #never mind unquoted att
        if nextSepPos == -1: #no other attribute
            attDef = attsStr
            rest = ''
        elif sepChr == self._ATT_CHR and eqPos < nextSepPos and eqPos != -1:
            endValPos = attsStr.find(self._ATT_QUOTE_CHR, eqPos + 2)
            attDef = attsStr[:endValPos+1]
            rest = attsStr[endValPos+1:]
        else:
            attDef = attsStr[:nextSepPos]
            rest = attsStr[nextSepPos:]
        attVal = attDef
        if sepChr == self._CLS_CHR:
            attKey = 'class'
        elif sepChr == self._ID_CHR:
            attKey = 'id'
        elif sepChr == self._ATT_CHR:
            attKey, attVal = self._parseGenAttr(attDef)
        else:
            raise(UnexpectedError('something went wrong'))
        return (attKey, attVal, rest)


    def _tagRestSplit(self, tagStr):
        "splits off tagName from tagStr"
        match = self.TAG_PART_SEPARATORS.search(tagStr)
        if match:
            pos = match.span()[0]
            tag = tagStr[:pos]
            rest = tagStr[pos:]
        else:
            pos = -1
            tag = tagStr
            rest = ''
        if not tag: 
            tag = 'div'
        return tag, rest

    def _getAtts(self, specStr):
        "gets all attr spec strings"
        if not specStr:
            return MultiDict()
        else:
            md = MultiDict()
            attKey, attVal, restStr = self._tagAttrSplit(specStr)
            md.insert(attKey, attVal)
        if restStr:
            md.update(self._getAtts(restStr))
        return md
    
    def _tagParse(self, tagStr):
        "parse a single tag"
        tagName, restStr = self._tagRestSplit(tagStr)
        attMultiDict = self._getAtts(restStr)
        return self.nodeFactory.mkElementNode(tagName, attMultiDict)

    def _decendingTagsParse(self, sameLevelStr):
        "parses a gpotentially multiple decending tags"
        tagStrL = self._tagDecendingSplit(sameLevelStr)
        tagEls = [self._tagParse(s) for s in tagStrL]
        linkNodes(tagEls)
        return tagEls[0]
    
    def _tagsParse(self, tagsStr):
        "parses a str containing potentially multiple tags"
        sameLevelStrL = self._tagSameLevelSplit(tagsStr)
        sameLevelEls = [self._decendingTagsParse(s) for s in sameLevelStrL]
        return sameLevelEls


    def _procElementTypeNodeRange(self, parentNode, lineRange):
        "processes an Element-type node"
        tagSpec, txt, isMultiLineTxt, txtStartPos = self._tagTextSplit(lineRange[0])
        sameLevelNodes = [] #initialize to avoid bomb in test below
        if isMultiLineTxt:  #mixed content is not supported
            txt = parseMultiLineTxt(txt, txtStartPos, lineRange[1:])
            lineRange = [] #it is consumed
        if tagSpec:
            sameLevelNodes = self._tagsParse(tagSpec)
            for n in sameLevelNodes:
                parentNode.addChild(n)
            txtBearingNode = sameLevelNodes[-1].lastNonTextNode()
        else:
            txtBearingNode = parentNode
        if txt:
            txtBearingNode.addChild(self.nodeFactory.mkTextNode(txt))
        if sameLevelNodes and len(lineRange) > 1:  #there's something to process
            self._procLines(sameLevelNodes[0], lineRange[1:])
    
    def _procSingleLineNodeRange(self, parentNode, lineRange):
        "processes nodes restricted to a single line"
        nodeSpec = lineRange[0].strip()
        node = self.nodeFactory.mkSingleLineNode(nodeSpec)
        parentNode.addChild(node)
        self._procLines(node, lineRange[1:])
 
    def _procSubRange(self, parentNode, lineRange):
        """updates parentNode as side effect
           this typically adds sub nodes
           processes a single sub lineRange
    
           first line defines what the content is
        """
        if not lineRange[0].strip(): #an empty line:
            self._procLines(parentNode, lineRange[1:])
        else:
            lineTypeChar = lineRange[0].lstrip()[0]
            if self.nodeFactory.isSingleLineNode(lineTypeChar):
                self._procSingleLineNodeRange(parentNode, lineRange)
            else:
                self._procElementTypeNodeRange(parentNode, lineRange)


    def _procLines(self, parentNode, lines):
        "processes lines under a given node"
        if lines:
            if not allLinesEmpty(lines):
                for lineRange in subRanges(lines):
                    self._procSubRange(parentNode, lineRange)
    
    
    def parseBuml(self, bumlStr):
        "parses a buml string and returns the root Node of a tree"
        lines = bumlStr.split('\n')
        #leave empty lines since valid in text
        #lines = [l for l in lines if l.strip()]
        lines = eliminateTabs(lines)
        #preprocess line continuations here
        rootNode = self.nodeFactory.mkRootNode()
        self._procLines(rootNode, lines)
        return rootNode

