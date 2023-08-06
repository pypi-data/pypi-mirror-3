from __future__ import absolute_import
from ..buml.inlineParser import *
from ..buml.inlineParser import _tagRestSplit
from ..buml.inlineMapper import InlineMapper
from ..buml.transformUtils import applyInlineMarkup

#def testNoseFindsMe():
#    "inlineParser: testNoseFindsMe"
#    assert 0

def test_orderedSepStrs():
    "inlineParser: orderedSepStrs"
    l=['*', ':::', '***', ':', '""', '**']
    print orderedSepStrs(l)
    assert orderedSepStrs(l) == [':::', ':', '***', '**', '*', '""']

def test_tagsPattern():
    "inlineParser: tagsPattern"
    p = tagsPattern(['a', 'b', 'c'])
    print p.pattern
    assert p.pattern == '^(.*?)(\\c|\\b|\\a)'
    p = tagsPattern(['b', 'a', 'c'])
    print p.pattern
    assert p.pattern == '^(.*?)(\\c|\\b|\\a)'

def test_endTagPattern():
    "inlineParser: endTagPattern"
    p = endTagPattern(']]', singleWord=True)
    expected = '^(\\S*?)(\]\])'
    print "computed: %s" % p.pattern
    print "expected: %s" % expected
    assert p.pattern == expected
    #--
    p = endTagPattern(']]', singleWord=False)
    expected = '^(.*?)(\]\])'
    print "computed: %s" % p.pattern
    print "expected: %s" % expected
    assert p.pattern == expected

def _findTagAssertion(inStr, patt, expected):
    print ">>%s<<" % inStr
    print patt.pattern
    res = findTag(patt, inStr)
    print "findTag:  pos=%s, txt='%s', tag='%s'" % res
    print "expected: pos=%s, txt='%s', tag='%s'" % expected
    print '--'
    assert res == expected

def test_findEndTag():
    "inlineParser: findStartTag"
    #--------------------------------
    #-- a single word
    patt = endTagPattern(']]', True)
    #--
    lineStr = 'single]] rest'
    expected = (8, 'single', ']]')
    _findTagAssertion(lineStr, patt, expected)
    #-
    lineStr = 'two words]] rest'
    expected = (-1, lineStr, '')
    _findTagAssertion(lineStr, patt, expected)
    #-
    lineStr = ']] rest'
    expected = (2, '', ']]')
    _findTagAssertion(lineStr, patt, expected)
    #--------------------------------
    #-- multiple words
    patt = endTagPattern(']]', False)
    #--
    lineStr = 'two words]] rest'
    expected = (11, 'two words', ']]')
    _findTagAssertion(lineStr, patt, expected)
    #--

def test_findStartTag():
    "inlineParser: findStartTag"
    tagL = ['**', '***', '::']
    patt = tagsPattern(tagL)
    #--
    lineStr = 'ads ***ital*** and **bold** and *ital* and ::repl:: cool'
    expected = (7, 'ads ', '***')
    _findTagAssertion(lineStr, patt, expected)
    #--
    tagL = ['::', '**', '***']
    patt = tagsPattern(tagL)
    lineStr = 'ads ***ital*** and **bold** and *ital* and ::repl:: cool'
    expected = (7, 'ads ', '***')
    _findTagAssertion(lineStr, patt, expected)
    #--
    lineStr = 'ads *ital* and **bold** and *ital* and ::repl:: cool'
    expected = (17, 'ads *ital* and ', '**')
    _findTagAssertion(lineStr, patt, expected)
    #--
    lineStr = '::ads ***ital*** and'
    expected = (2, '', '::')
    _findTagAssertion(lineStr, patt, expected)
    #--
    lineStr = 'nothing to be found here!'
    expected = (-1, lineStr, '')
    _findTagAssertion(lineStr, patt, expected)
    #--
    lineStr = 'this is on\nsecond **line**!'
    print 
    expected = (20, 'this is on\nsecond ', '**')
    _findTagAssertion(lineStr, patt, expected)

def test_tagRestSplit():
    "inlineParser: _tagRestSplit"
    spec = InlineMapper().mappingSpec()
    print spec.mappingDict().keys()
    s = 'leadingTxt **important** rest'
    print _tagRestSplit(s, spec)
    res = _tagRestSplit(s, spec)
    assert res == ('leadingTxt ', '**', 'important', ' rest')
    #--
    s = '**important** rest'
    print _tagRestSplit(s, spec)
    res = _tagRestSplit(s, spec)
    assert res == ('', '**', 'important', ' rest')
    #--
    s = 'leading **important]] rest'
    print _tagRestSplit(s, spec)
    res = _tagRestSplit(s, spec)
    assert res == ('leading **important]] rest', '', '', '')
    #--
    s = 'nothing to be found'
    print _tagRestSplit(s, spec)
    res = _tagRestSplit(s, spec)
    assert res == ('nothing to be found', '', '', '')

def test_parser():
    "inlineParser: parser"
    spec = InlineMapper().mappingSpec()
    s = 'hello *there* **bold** [[guy <http://guy.org]] over there'
    nodeL = parse(s, spec)
    for node in nodeL:
        node.pprint()
        print
    assert nodeL[0].__class__.__name__ == 'Text'
    assert nodeL[0].txt == 'hello '
    assert nodeL[1].tag == 'em'
    assert nodeL[1][0].__class__.__name__ == 'Text'
    assert nodeL[1][0].txt == 'there'
    assert nodeL[2].__class__.__name__ == 'Text'
    assert nodeL[2].txt == ' '
    assert nodeL[3].tag == 'strong'
    assert nodeL[3][0].__class__.__name__ == 'Text'
    assert nodeL[3][0].txt == 'bold'
    assert nodeL[4].__class__.__name__ == 'Text'
    assert nodeL[4].txt == ' '
    assert nodeL[5].tag == 'a'
    assert nodeL[5].atts['href'] == ['http://guy.org']
    assert nodeL[5][0].__class__.__name__ == 'Text'
    assert nodeL[5][0].txt == 'guy'
    assert nodeL[6].__class__.__name__ == 'Text'
    assert nodeL[6].txt == ' over there'
    #--
    s = 'please, ::replace:: this'
    nodeL = parse(s, spec)
    print '--------'
    for node in nodeL:
        node.pprint()
    assert nodeL[0].__class__.__name__ == 'Text'
    assert nodeL[0].txt == 'please, '
    assert nodeL[1].tag == 'replace'
    assert nodeL[1][0].__class__.__name__ == 'Text'
    assert nodeL[1][0].txt == 'replace'
    #-- 
    s = 'non * matching endTag ::match:: end'
    nodeL = parse(s, spec)
    print ">> nodeL: ", nodeL
    print '--------'
    for node in nodeL:
        node.pprint()
    assert nodeL[0].__class__.__name__ == 'Text'
    assert nodeL[0].txt == 'non * matching endTag '
    assert nodeL[1].tag == 'replace'
    s = 'non * matching endTag and no more tags'
    nodeL = parse(s, spec)
    print '--------'
    for node in nodeL:
        node.pprint()
    assert nodeL[0].__class__.__name__ == 'Text'
    assert nodeL[0].txt == 'non * matching endTag and no more tags'

def test_parserRecursion():
    "inlineParser: parser recursive decend"
    spec = InlineMapper().mappingSpec()
    s = 'hello ** bold *buml ::replMe:: markup* good-bye**'
    nodeL = parse(s, spec)
    for node in nodeL:
        node.pprint()
    assert nodeL[0].__class__.__name__ == 'Text'
    assert nodeL[0].txt == 'hello '
    assert nodeL[1].__class__.__name__ == 'Element'
    assert nodeL[1].tag == 'strong'
    assert nodeL[1][0].__class__.__name__ == 'Text'
    assert nodeL[1][0].txt == ' bold '
    assert nodeL[1][2].__class__.__name__ == 'Text'
    assert nodeL[1][2].txt == ' good-bye'
    assert nodeL[1][1].__class__.__name__ == 'Element'
    assert nodeL[1][1].tag == 'em'
    assert nodeL[1][1][0].__class__.__name__ == 'Text'
    assert nodeL[1][1][0].txt == 'buml '
    assert nodeL[1][1][2].__class__.__name__ == 'Text'
    assert nodeL[1][1][2].txt == ' markup'
    assert nodeL[1][1][1].__class__.__name__ == 'Element'
    assert nodeL[1][1][1].tag == 'replace'
    assert nodeL[1][1][1][0].__class__.__name__ == 'Text'
    assert nodeL[1][1][1][0].txt == 'replMe'


def test_applyInlineMarkup():
    "inlineParser: transformUtils.applyInlineMarkup"
    im = InlineMapper()
    spec= im.mappingSpec()
    nf = im.nodeFactory
    el = nf.mkElementNode('div')
    s = 'hello ** bold *buml ::replMe:: markup* good-bye**'
    txtN = nf.mkTextNode(s)
    el.addChild(txtN)
    #-- 
    print "before:"
    print el.pprint()
    applyInlineMarkup(el, spec)
    print "after:"
    print el.pprint()
    assert el.__class__.__name__ == 'Element'
    assert el.tag == 'div'
    nodeL = el.children #so I can copy assertions from above
    assert nodeL[0].__class__.__name__ == 'Text'
    assert nodeL[0].txt == 'hello '
    assert nodeL[1].__class__.__name__ == 'Element'
    assert nodeL[1].tag == 'strong'
    assert nodeL[1][0].__class__.__name__ == 'Text'
    assert nodeL[1][0].txt == ' bold '
    assert nodeL[1][2].__class__.__name__ == 'Text'
    assert nodeL[1][2].txt == ' good-bye'
    assert nodeL[1][1].__class__.__name__ == 'Element'
    assert nodeL[1][1].tag == 'em'
    assert nodeL[1][1][0].__class__.__name__ == 'Text'
    assert nodeL[1][1][0].txt == 'buml '
    assert nodeL[1][1][2].__class__.__name__ == 'Text'
    assert nodeL[1][1][2].txt == ' markup'
    assert nodeL[1][1][1].__class__.__name__ == 'Element'
    assert nodeL[1][1][1].tag == 'replace'
    assert nodeL[1][1][1][0].__class__.__name__ == 'Text'
    assert nodeL[1][1][1][0].txt == 'replMe'

