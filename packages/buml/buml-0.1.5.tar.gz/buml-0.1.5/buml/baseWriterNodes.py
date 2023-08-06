#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
===============
baseWriterNodes
===============

This module is a part of *buml*.

:Author and Copyright:  Bud P. Bruegger
:License:               FreeBSD

This module extends the Nodes defined in baseNodes with methods to write them
out to a text (xml, html, etc.).  

The separation of this functionality into a separate module allows for easy
customization of writers through subclassing or the use of alternative writers.  
The default behavior of Node.xml() is to do pretty printing of the content.
This inserts whitespace.  Should this not be desired, it is possible to avoid
pretty printing and whitespace by calling node.xml(indenWidth=0, joinChar='')

Use config* utility functions to configure the writer after import
"""

from copy import deepcopy
import baseNodes
from utilities import warning 

#== config and config functions ===========================================
PRETTY_INDENT_WIDTH = 2
DEFAULT_MAX_SINGLE_LINE_LEN = 40
#=================================================================

class Node(baseNodes.Node):
    #abstract node should render as empty string

    #-- configuration --------
    _EMPTY_EL_CLOSURE_STR = '/'
    _JOIN_CHAR = '\n'
    _INDENT_WIDTH = PRETTY_INDENT_WIDTH
    _MAX_SINGLE_LINE_LEN = DEFAULT_MAX_SINGLE_LINE_LEN

    @classmethod
    def setEmptyElementMode(cls, mode=''):
        if mode not in ['xml', 'sgml', 'compat']:
            warning("mode must be one of ['xml', 'sgml', 'compat']")
        elif mode == 'xml':
            Node._EMPTY_EL_CLOSURE_STR = '/'
        elif mode == 'sgml':
            Node._EMPTY_EL_CLOSURE_STR = ''
        elif mode == 'compat':
            Node._EMPTY_EL_CLOSURE_STR = ' /'

    @classmethod
    def setRenderMode(cls, mode='', prettyIndentWidth=PRETTY_INDENT_WIDTH):
        if mode not in ['pretty', 'noWhiteSpace']:
            warning("mode must be one of ['pretty', 'noWhiteSpace']")
        elif mode == 'pretty':
            Node._JOIN_CHAR = '\n'
            Node._INDENT_WIDTH = prettyIndentWidth
        elif mode == 'noWhiteSpace':
            Node._JOIN_CHAR = ''
            Node._INDENT_WIDTH = 0

    @classmethod
    def setMaxSingleLineLen(cls, maxlen):
        #  How long can a single line text be to be kept 
        #  on same line with end tag
        Node._MAX_SINGLE_LINE_LEN = maxlen
    #-- end config ------

    def startTag(self):
        return '' # specialize in subclasses

    def endTag(self):
        return '' # specialize in subclasses

    def emptyTag(self):
        return '' # specialize in subclasses where needed

    def xmlLchildren(self):
        l = []
        l.append(self.startTag())
        l.append([c.xmlL() for c in self.children])
        l.append(self.endTag())
        return l

    def xmlLtxt(self):
        l = ["%s%s%s" % (self.startTag(), self.txt, self.endTag())]
        if self.children:
            l.append([c.xmlL() for c in self.children])
        return l

    def xmlLempty(self):
        return [self.emptyTag()]

    def xmlL(self):
        "returns a list of strings"
        if self.txt: #even if it has children! Must come first!
            return self.xmlLtxt()
        if self.children:
            return self.xmlLchildren()
        return self.xmlLempty()

    def indentedStr(self, str, indentLevel):
        # //2 since two lists wrappers per step
        indentStr = indentLevel * self._INDENT_WIDTH // 2 * ' '
        l = []
        for line in str.split('\n'):
            l.append('%s%s' % (indentStr, line))
        return "\n".join(l)

    def prettyXmlL(self, xmlL, indentLevel):
        l = []
        for el in xmlL:
            if type(el) == type([]):
                l.append(self.prettyXmlL(el, indentLevel+1))
            else: # a string
                l.append(self.indentedStr(el, indentLevel))
        return self._JOIN_CHAR.join(l)

    def xml(self, initialIndentLevel=-2):
        "initialIndentLevel -1 since there is a 'silent' Node as root"
        clone = deepcopy(self)
        #short text content rendered on single line
        txtNodes = clone.findAllNodes('Text')
        for n in txtNodes:
            if not '\n' in n.txt \
               and len(n.txt) < self._MAX_SINGLE_LINE_LEN \
               and len(n.parent.children) == 1:
                n.parent.txt = n.txt
                n.parent.children = ''
        #no whitespace in CDATA
        cdataNodes = clone.findAllNodes('CDATA')
        for n in cdataNodes:
            if n.children:
                n.txt = n.children[0].txt
                n.children = []
        #remove BumlComments:
        comments = clone.findAllNodes('BumlComment')
        for n in comments:
            n.parent.children.remove(n)
        return self.prettyXmlL(clone.xmlL(), initialIndentLevel).strip()


class BumlComment(baseNodes.GenEl, Node):
    pass

class Element(baseNodes.GenEl, Node):

    def singleAttStr(self, key, valL):
        valStr = ' '.join(valL)
        return '%s="%s"' % (key, valStr)

    def attStr(self):
        attL = [self.singleAttStr(k, v) for k, v in self.atts.items()]
        return ' '.join(attL)

    def tagStr(self):
        l = [self.tag]
        attStr = self.attStr()
        if attStr:  l.append(attStr)
        return ' '.join(l)

    def startTag(self):
        return '<%s>' % self.tagStr()

    def endTag(self):
        return '</%s>' % self.tag

    def emptyTag(self):
        return '<%s%s>' % (self.tagStr(), self._EMPTY_EL_CLOSURE_STR)

class ProcessingInstruction(Element):

    def emptyTag(self):
        return '<?%s?>' % self.tagStr()

    def startTag(self):
        return '<?%s ' % self.tagStr()

    def endTag(self):
        return ' ?>'

class Text(baseNodes.Text, Node):
    pass

class XmlComment(baseNodes.GenEl, Node):
    def startTag(self):
        return '<!-- '

    def endTag(self):
        return ' -->'

class DocTypeDecl(baseNodes.GenEl, Node):
    def startTag(self):
        return '<!'

    def endTag(self):
        return '>'

class CDATA(baseNodes.GenEl, Node):
    def startTag(self):
        return '<![CDATA['

    def endTag(self):
        return ']]>'

class Template(baseNodes.GenEl, Node):
    def startTag(self):
        return '{%s ' % self.tag

    def endTag(self):
        if self.tag == '%':
            return ' %}'
        elif self.tag == '{':
            return ' }}'
        else:
            warning('Unknown Template Type %s for "%s"' % (self.tag, self.txt))
            #trying anyhow:
            return ' %s}' % self.tag

class Macro(baseNodes.GenEl, Node):
    def startTag(self):
        return '*['

    def endTag(self):
        return ']*'

