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

What is actually done by the parser depends on a mappingSpec as typically
provided by the mappingSpec method of the inlineMapper.InlineMapper.  

The parser can be applied to a tree of nodes using
tranformUtils.applyInlineMarkup.
"""

#  ToDo:
#  ----
#  
#  * support for quoting special characters with \

import re
from utilities import reQuote

#============================================================

def endTagPattern(endTag, singleWord):
    """
    matches any text (non-greedy) from start to endTag.
    Single word restricts match to a single word
    """
    if singleWord: 
        txtChr = '\\S'
    else:
        txtChr = '.'
    patternStr = '^(%s*?)(%s)' % (txtChr, reQuote(endTag))
    return re.compile(patternStr, re.DOTALL)

def orderedSepStrs(sepStrL):
    "orderes such that higher repetitions of the same char come first"
    # ['*', '**'] is bad,  ['**', '*'] works
    # this is necessary to make the re match "greedy"
    l = sepStrL[:]  #a copy
    if '' in l:
        l.remove('')
    l.sort()
    l.reverse()
    return l

def tagsPattern(tags):
    "returns a compiled re pattern to match the first tag"
    tags = orderedSepStrs(tags)
    return reStartTagPattern(tags)


def reStartTagPattern(tagL):
    "returns an re pattern that matches any string in the list"
    tagL = [reQuote(s) for s in tagL]
    patternStr = '^(.*?)(%s)' % '|'.join(tagL)
    patt = re.compile(patternStr, re.DOTALL)
    return patt


def findTag(tagPattern, lineStr):
    """
     returns the end position of all matched text (or -1 if no match), 
     the leadingTxt, and matched tag"
    """
    match = tagPattern.match(lineStr)
    if match is not None:
        txt, tag = match.groups()
        return (match.end(), txt, tag)
    else:
        return (-1, lineStr, '')
    
def _tagRestSplit(txtStr, mappingSpec):
    "splits of first (leadingTxt, tag, tagContent, rest) from rest of txtStr"
    startTagEndPos, leadingTxt, tag = findTag(mappingSpec.startTagPattern(), txtStr)
    if startTagEndPos == -1:
        return (txtStr, '', '', '')
    else:
        restStr = txtStr[startTagEndPos:]
        endTagEndPos, content, endTag = findTag(mappingSpec.mappingDict()[tag].endTagPattern, \
                                          restStr)
        if endTagEndPos == -1:
            leadingTxtOfRest, tag, content, restStr = _tagRestSplit(restStr, mappingSpec)
            return (txtStr[:startTagEndPos] + leadingTxtOfRest, tag, content, restStr)
        else:
            return (leadingTxt, tag, content, restStr[endTagEndPos:])

def parse(txt, mappingSpec):
    "parses txt and returns ElementNodes"
    specDict = mappingSpec.mappingDict()
    rest = txt
    nodeL = []
    while rest:
        leadingTxt, tag, content, rest = _tagRestSplit(rest, mappingSpec)
        if leadingTxt:
            nodeL.extend(specDict[''].handler(leadingTxt))
        if tag:
            nodeL.extend(specDict[tag].handler(content))
    return nodeL
