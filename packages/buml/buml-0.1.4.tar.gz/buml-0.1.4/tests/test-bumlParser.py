from __future__ import absolute_import
from ..buml.bumlParser import *


#def testNoseFindsMe():
#    "bumlParser: testNoseFindsMe"
#    assert 0


def testTabs():                    
    """bumlParser: tab substitution"""
    l=['\t\txxx']
    assert eliminateTabs(l) == ['        xxx']
    l=['  \txxx']
    assert eliminateTabs(l) == ['      xxx']
    l=['\txxx\t']
    assert eliminateTabs(l) == ['    xxx\t']
    l="""  xx\n  \t  yy\n\n  zz\t\t""".split('\n')
    r="""  xx\n        yy\n\n  zz\t\t""".split('\n')
    assert eliminateTabs(l) == r

def testIndent():                    
    """bumlParser: indentParsing"""
    s="   xx yy zz "
    assert indent(s) == 3

def testSubRanges():                    
    """bumlParser: subLineRange and subRanges"""
    #empty lines:  not possible, eliminated as pre-condition
    l = ["hello", "  there", "     how", "  are", "     you ", 
         "       doing", "Bud"]
    mono = ["hello", "  there", "     how", "  are", "     you ", 
            "       doing"]
    rest = ['Bud']
    assert subLineRange(l) == (mono, rest)
    l = ["hello"]
    assert subLineRange(l) == (['hello'], [])
    l = ["  hello", "    one", "    two", "  there", 
         "  buddy", "    over", "      there"]
    r1 = ["  hello", "    one", "    two"]
    r2 = ["  there"]
    r3 = ["  buddy", "    over", "      there"]
    assert subRanges(l) == ([r1, r2, r3])
    l = ["  hello", "", "    one", "", "  there"]
    r1 = ["  hello", "", "    one", ""]
    r2 = ["  there"]
    assert subRanges(l) == ([r1, r2])


def testTagTextSplit():                    
    """bumlParser: tab text splitting"""
    p=Parser()
    s="""  div.cool@title='two words' otherTag#id1 "text here"""
    tag="div.cool@title='two words' otherTag#id1"
    txt='text here'
    assert p._tagTextSplit(s) == (tag, txt, False, 43)
    s="""  div.cool  otherTag#id1"""
    tag="""div.cool  otherTag#id1"""
    txt=''
    assert p._tagTextSplit(s) == (tag, txt, False, -1)
    s='  div.cool  otherTag#id1 """start of multiline text'
    tag='div.cool  otherTag#id1'
    txt='start of multiline text'
    assert p._tagTextSplit(s) == (tag, txt, True, 28)
    s='    """only start of multiline text'
    tag=''
    txt='only start of multiline text'
    assert p._tagTextSplit(s) == (tag, txt, True, 7)
    s='   "only start of text  '
    tag=''
    txt='only start of text  '
    assert p._tagTextSplit(s) == (tag, txt, False, 4)

def testTagRestSplit():
    """bumlParser: tagRestSplit"""
    p=Parser()
    s="span.blue"
    assert p._tagRestSplit(s) == ('span', '.blue')
    s="div"
    assert p._tagRestSplit(s) == ('div', '')
    s=".blue"
    assert p._tagRestSplit(s) == ('div', '.blue')

def testTagAttrSplit():
    """bumlParser: tagAttrSplit"""
    p=Parser()
    s=".cool#id1@title='x'"
    assert p._tagAttrSplit(s) == ('class', 'cool', "#id1@title='x'")
    s="#id1@title='x'"
    assert p._tagAttrSplit(s) == ('id', 'id1', "@title='x'")
    s="@title='x'.hello"
    assert p._tagAttrSplit(s) == ('title', 'x', ".hello")
    s="@title='x'"
    assert p._tagAttrSplit(s) == ('title', 'x', "")
    s="@src='img.png'.cl1"
    assert p._tagAttrSplit(s) == ('src', 'img.png', ".cl1")
    s="@href='else#where'#id1"
    assert p._tagAttrSplit(s) == ('href', 'else#where', "#id1")
    s="@mail='user@gmail.com'@other=xy"
    assert p._tagAttrSplit(s) == ('mail', 'user@gmail.com', "@other=xy")

def testTagParse():
    """bumlParser: tagParse"""
    p=Parser()
    s='.hello'
    el = p._tagParse(s)
    assert el.tag == 'div'
    assert el.attDict()['class'] == ['hello']
    s='span#id1'
    el = p._tagParse(s)
    assert el.tag == 'span'
    assert el.attDict()['id'] == ['id1']

def testTagsParse():
    """tagsParse"""
    p = Parser()
    s='.hello > .blue > ul.big>li#id3'
    els = p._tagsParse(s)
    assert len(els) == 1
    assert els[0].tag == 'div'
    assert els[0][0].tag == 'div'
    assert els[0][0][0].tag == 'ul'
    assert els[0][0][0][0].tag == 'li'
    assert els[0][0][0][0].attDict() == {'id':['id3']}
    s='.hello > .blue & br&ul>li'
    els = p._tagsParse(s)
    assert els[0].tag == 'div'
    assert els[1].tag == 'br'
    assert els[2].tag == 'ul'
    assert els[2][0].tag == 'li'
    assert els[2][0].children == []

def testGetAtts():
    """bumlParser: getAtts"""
    p=Parser()
    s=".cool#id1@title='x'"
    md = MultiDict({'class' : 'cool', 'id': 'id1', 'title': 'x'})
    assert p._getAtts(s) == md
    s=".cool#id1.cooler.coolest"
    md = MultiDict({'class' : 'cool', 'id': 'id1'})
    md.insert("class", 'cooler')
    md.insert("class", 'coolest')
    assert p._getAtts(s) == md

def testParseGenAttr():
    """bumlParser: parseGenAttr"""
    p = Parser()
    s="title=hello"
    assert p._parseGenAttr(s) == ('title', 'hello')
    s="words='one and two'"
    assert p._parseGenAttr(s) == ('words', 'one and two')
    s="flag"
    assert p._parseGenAttr(s) == ('flag', 'True')

def testTagDecendingSplit():
    """bumlParser: tagDecendingSplit"""
    p = Parser()
    s="div.cool > #id1> table>tbody.xx>trow#n1"
    l = ["div.cool", "#id1", "table", "tbody.xx", "trow#n1"]
    assert p._tagDecendingSplit(s) == l

def testTagSameLevelSplit():
    """bumlParser: tagSameLevelSplit"""
    p = Parser()
    s="div.cool > #id1 & br & ul>li.odd"
    l = ["div.cool > #id1", "br", "ul>li.odd"]
    assert p._tagSameLevelSplit(s) == l

def testParseMultiLineTxt():
    """bumlParser: parseMultiLineTxt """
    p = Parser()
    l = ['       =text starts here  ',
         '        and goes over multiple\t',
         '   ',
         '        lines that are lined up  ',
         '          or  ',
         '            indent',
         '              as they want']
    startPos = 8
    firstLine = l[0][startPos:]
    txt = parseMultiLineTxt(firstLine, startPos, l[1:])
    x = ['text starts here  ',
         'and goes over multiple\t',
         '',
         'lines that are lined up  ',
         '  or  ',
         '    indent',
         '      as they want']
    t = '\n'.join(x)
    assert txt == t

def test_nodeFactoryPassing():
    "bumlParser: nodeFactoryPassing"
    p = Parser()
    assert p.nodeFactory.__class__.__name__ == "NodeFactory"
    class FakeNodeFactory:
        pass
    fnf = FakeNodeFactory()
    pp = Parser(fnf)
    print pp.nodeFactory.__class__.__name__ 
    assert pp.nodeFactory.__class__.__name__ == "FakeNodeFactory"

def test_updateAfterReConfig():
    "bumlParser: updateAfterReConfig"
    p = Parser()
    patt1 = p.TAG_PART_SEPARATORS.pattern
    p._SAME_LEV_SEP = '+'
    p.updateAfterReConfig()
    patt2 = p.TAG_PART_SEPARATORS.pattern
    assert patt1 == patt2 #_SAME_LEV_SEP not part of pattern
    p._ID_CHR = '$'
    p.updateAfterReConfig()
    patt3 = p.TAG_PART_SEPARATORS.pattern
    print patt1
    print patt3
    assert patt1 == '[\#\.\@]'
    assert patt3 == '[\$\.\@]'


    
