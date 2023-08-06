#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
=============
bumdProcessor
=============

This module is a part of *buml*.

:Author and Copyright:  Bud P. Bruegger
:License:               FreeBSD

Unittests for buml
"""
from __future__ import absolute_import

import unittest
from ..buml.bumlParser import Parser

#== Tests ========================================

#def testNoseFindsMe():
#    "test-all: Nose Finds Me"
#    assert 0

def test_allowedCharacters():
    "all: tests allowed characters"
    p = Parser()
    l = []
    #-- any char but " in lineText of simpleEl: (bumlComment)
    s = """/ buml comment " \' & > . # @  / \\ !"""
    o = ""
    l.append((s, o))
    #-- start normally commented section----------------------
    #-- pre: single line el > is declared by nodeFactory
    #-- uncomment this only if you uncomment the corresponding
    #   modifications in nodeFactory
    #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    #-- any char but " as specialChar of simpleEl:
    # s = """> very special singleLineEl " \' & > . # @ """
    # o = """<!-- very special singleLineEl " \' & > . # @ -->"""
    # l.append((s, o))
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #-- any char but " in lineText of simpleEl: (XmlComment)
    s = """! very special singleLineEl " \' & > . # @ / \\ ! """
    o = """<!-- very special singleLineEl " \' & > . # @ / \\ ! -->"""
    l.append((s, o))
    #--
    #-- start normally commented section----------------------
    #-- pre: disable validity checking in nodeFactory
    #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    #-- any character but " & > . # @ in elName
    #s = """elName/\!:= blank"""
    #o = """<elName/\\!:= blank/>"""
    #l.append((s, o))
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #-- any character but " & > . # @ = in attName
    s = """ @start ' / \\ ! : - end"""
    o = """ <div start ' / \\ ! : - end="True"/>"""
    l.append((s, o))
    #-- any character but " & > . # @ in unQuotedAttVal
    s = """ .start ' / \\ ! : - < end"""
    o = """ <div class="start ' / \\ ! : - < end"/>"""
    l.append((s, o))
    #-- any character but " & > ' in quotedAttVal
    s = """@att='start / \\ ! : - < . # @ end'"""
    o = """ <div att="start / \\ ! : - < . # @ end"/>"""
    l.append((s, o))
    #---------------------------------
    for (s, o) in l:
        s = s.replace("'''", '"""')
        o = o.strip()
        out = p.parseBuml(s).xml().strip()
        print "out : %s" % out
        print "o   : %s" % o
        assert out == o

def test_emptyElementMode():
    """all: emptyElementMode"""
    p = Parser()
    rootN = p.parseBuml("br")
    rootN.setEmptyElementMode('sgml')
    out = rootN.xml().strip()
    print out
    assert out == "<br>"
    #--
    rootN.setEmptyElementMode('xml')
    out = rootN.xml().strip()
    print out
    assert out == "<br/>"
    #--
    rootN.setEmptyElementMode('compat')
    out = rootN.xml().strip()
    print out
    assert out == "<br />"



def test_ParserAll():
    """all: parser b2x examples"""
    #--
    p = Parser()
    #-- configuration that is expected in the tests!!!
    dummy = p.parseBuml('br')
    dummy.setEmptyElementMode('xml')
    dummy.setRenderMode('pretty', 2)
    #--
    l = []
    s = "/a buml comment"
    x = ""
    l.append((s, x))
    s = "! an html comment"
    x = '<!-- an html comment -->'
    l.append((s, x))
    s = """
html
  body
    h1 "Welcome to buml
    p '''This is text
         that spans
         multiple lines""" 
    x = """
<html>
  <body>
    <h1>Welcome to buml</h1>
    <p>
      This is text
      that spans
      multiple lines
    </p>
  </body>
</html>"""
    l.append((s, x))
    s = 'p.cool "This is a cool paragraph\n' + \
        'p.cool.blue "this has two classes'
    x = '<p class="cool">This is a cool paragraph</p>\n' + \
        '<p class="cool blue">this has two classes</p>'
    l.append((s, x))
    s = 'div#navbar "bar here'
    x = '<div id="navbar">bar here</div>'
    l.append((s, x))
    s = "\n".join([
        """h1@myAttr=something "title 1""", 
        """h2@att2='two words' "title 2""", 
        """img@src='me.png'""", 
        """a@href='else#where' "go""", 
        """h3@flag "set to True""",
        """h4@a1=v1@a2=v2 "two attributes""" ])
    x =  "\n".join([
        '<h1 myAttr="something">title 1</h1>',
        '<h2 att2="two words">title 2</h2>',
        '<img src="me.png"/>',
        '<a href="else#where">go</a>',
        '<h3 flag="True">set to True</h3>',
        '<h4 a1="v1" a2="v2">two attributes</h4>' ])
    l.append((s, x))
    s = '.class1 "A dev element\n#id1 "this too'
    x = '<div class="class1">A dev element</div>\n' + \
        '<div id="id1">this too</div>'
    l.append((s, x))
    s = '.cl1#id1@att1=v1.cl2 "all mixed'
    x = '<div class="cl1 cl2" att1="v1" id="id1">all mixed</div>'
    l.append((s, x))
    s = 'br\nhr'
    x = '<br/>\n<hr/>'
    l.append((s, x))
    s = """ul > li > a@href='this.html' "first item\n""" + \
          '  li "second item'
    x = '<ul>\n  <li>\n    <a href="this.html">first item</a>\n' + \
        '  </li>\n  <li>second item</li>\n</ul>'
    l.append((s, x))
    s = 'br & br & hr & br'
    x = '<br/>\n<br/>\n<hr/>\n<br/>'
    l.append((s, x))
    s = """div > img@src='me.png' & br & br & ul > li "only one item"""
    x = '<div>\n  <img src="me.png"/>\n</div>\n' + \
        '<br/>\n<br/>\n<ul>\n  <li>only one item</li>\n</ul>'
    l.append((s, x))
    s = 'p\n' + \
        '  "this is a first line\n' + \
        '  em "something emphasized\n' + \
        '  " and\n' + \
        '  strong "something strong\n' + \
        '  "and some tail'
    x = '<p>\n' + \
        '  this is a first line\n' + \
        '  <em>something emphasized</em>\n' + \
        '   and\n' + \
        '  <strong>something strong</strong>\n' + \
        '  and some tail\n' + \
        '</p>'
    l.append((s, x))

    s = """
.cooltext '''asdf 0708 ~!@#$%^&*()_+`\|/?,./<>-=_+
             and even " and ''' without closing anything"""
    x = """
<div class="cooltext">
  asdf 0708 ~!@#$%^&*()_+`\|/?,./<>-=_+
  and even " and ''' without closing anything
</div> """
    s = s.replace("'''", '"""')
    x = x.replace("'''", '"""')
    l.append((s, x))
    s = """
.indent '''and empty lines:
         
           and any kind of indentation
             relative 
               to 
                 the
              start
                of 
           the 
                      first
             line"""
    x = """
<div class="indent">
  and empty lines:
  
  and any kind of indentation
    relative 
      to 
        the
     start
       of 
  the 
             first
    line
</div> """
    s = s.replace("'''", '"""')
    l.append((s, x))
    s = """
div '''<em>evidently</em> you can
       embedd <html></html> like
       <a href="http://bruegger.it">visit</a>"""
    x = """
<div>
  <em>evidently</em> you can
  embedd <html></html> like
  <a href="http://bruegger.it">visit</a>
</div>"""
    s = s.replace("'''", '"""')
    l.append((s, x))

    s = """
div '''and you can use *inline* **markup**
       like `reStructured Text 
       <http://docutils.sourceforge.net/rst.htm>`_

       ..topic:: Interesting
   
          That you can pass to some
          configurable **inline parser**"""
    x = """
<div>
  and you can use *inline* **markup**
  like `reStructured Text 
  <http://docutils.sourceforge.net/rst.htm>`_
  
  ..topic:: Interesting
  
     That you can pass to some
     configurable **inline parser**
</div>"""
    s = s.replace("'''", '"""')
    l.append((s, x))
    s = """
{% these are treated
   {{ just like normal elements"""
    x = """
{% these are treated %}
  {{ just like normal elements }}"""
    l.append((s, x))

    s = """
        """
    x = """
        """
    s = s.replace("'''", '"""')
    l.append((s, x))

    s = """
        """
    x = """
        """
    s = s.replace("'''", '"""')
    l.append((s, x))
    s = ''
    x = ''
    l.append((s, x))
    s = ''
    x = ''
    l.append((s, x))
    #----------
    for (s, x) in l:
        s = s.replace("'''", '"""')
        x = x.strip()
        out = p.parseBuml(s).xml().strip()
        print "=========="
        print out
        print "------"
        print x
        assert out == x
