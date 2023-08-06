from __future__ import absolute_import
from ..buml.baseNodes import *
import unittest

#def testNoseFindsMe():
#    "baseNodes: testNoseFindsMe"
#    assert 0

def test_various():
    "baseNodes: various"
    # to improve coverage
    n = Node()
    print n
    assert n.__repr__() == "<Node instance: I'm the root>"
    e = GenEl('el')
    print e
    assert e.__repr__() == "<el GenEl>"
    e.addAttr('x', 'X')
    print e.__repr__()
    assert e.__repr__() == "<el GenEl: {'x': ['X']}>"
    class MyEl(GenEl):
        pass
    me = MyEl('I')
    assert me.__repr__() == "<I MyEl>"

    #--
    m1 = MultiDict({'x': 'X'})
    m2 = MultiDict({'x': 'X'})
    assert m1 == m2
    #--
    n.addChild(e)
    print n.asNestedList()
    #assert n.asNestedList() == [n, [[e]]]
    assert n.asNestedList() == [n, [e]]
    e2 = GenEl('e2')
    n.addChild(e2)
    print n.asNestedList()
    assert n.asNestedList() == [n, [e, e2]]
    e3 = GenEl('e3')
    e2.addChild(e3)
    print n.asNestedList()
    assert n.asNestedList() == [n, [e, [e2, [e3]]]]

def test_GenElConstruction():
    "baseNodes: GenEl with dict or MultiDict as atts"
    #--dict
    e = GenEl('e', atts={'x':'X'})
    print e.attDict()
    assert e.attDict() == {'x': ['X']}
    #--MultiDict
    md = MultiDict({'x':'X'})
    e = GenEl('e', atts=md)
    assert e.attDict() == {'x': ['X']}
    #--empty
    e = GenEl('e')
    assert e.attDict() == {}

def test_replaceWith():
    "baseNodes: replaceWith"
    #replace with a single node
    root = Node()
    e1 = GenEl('e1')
    root.addChild(e1)
    e1a = GenEl('e1a')
    e1b = GenEl('e1b')
    e1.addChild(e1a)
    e1.addChild(e1b)
    e2 = GenEl('e2')
    root.addChild(e2)
    sn = GenEl('substNode')
    e1.replaceWith(sn)
    print root.pprint()
    assert root.children[0] == sn
    assert root.children[1] == e2
    assert sn.parent == root
    assert sn.children == [e1a, e1b]
    assert e1a.parent == sn
    assert e1b.parent == sn
    #replace with a list of nodes
    sn1 = GenEl('substN1')
    sn2 = GenEl('substN2')
    sn3 = GenEl('substN3')
    sn.replaceWith([sn1, sn2, sn3])
    print root.pprint()
    assert root.children[0] == sn1
    assert root.children[1] == sn2
    assert root.children[2] == sn3
    assert root.children[3] == e2
    assert sn1.parent == root
    assert sn2.parent == root
    assert sn3.parent == root
    assert sn1.children == [e1a, e1b]
    assert e1a.parent == sn1
    assert e1b.parent == sn1



#== Tests ========================================
class UtilityTests(unittest.TestCase):        

#    def testNoseFindsMe(self):
#        "testNoseFindsMe: baseNodes"
#        self.assertTrue(False)

    def sentinel(self):
        "use to see if nosetest picks it up"
        self.assertTrue(False)
    
    def testMultiDict2(self):                    
        """MultiDict2"""
        d = MultiDict()
        self.assertFalse(bool(d))
        d['x'] = 'X'
        self.assertTrue(bool(d))

    def testMultiDict(self):                    
        """MultiDict"""
        d = MultiDict()
        self.assertEqual(d.asDict(), {})
        d.insert('a', 'A')
        d.insert('b', 'B')
        self.assertEqual(d.asDict(), {'a': ['A'], 'b': ['B']})
        d.insert('b', 'B2')
        self.assertEqual(d.asDict(), {'a': ['A'], 'b': ['B', 'B2']})
        self.assertEqual(d.items(), [('a', ['A']), ('b', ['B', 'B2'])])
        dd = MultiDict()
        dd.insert('a', 'A')
        dd.insert('a', 'A2')
        dd.insert('c', 'C')
        d.update(dd)
        self.assertEqual(d.asDict(), {'a': ['A', 'A', 'A2'], 
                                  'b': ['B', 'B2'],
                                  'c': ['C']})
        #-- from dict
        ddd = MultiDict({'x': 'X', 'y': 'Y'})
        self.assertEqual(ddd.asDict(), {'x': ['X'], 'y': ['Y']})
        #-- cloning
        md = MultiDict({'hello': 'goodbye'})
        md1 = md.clone()
        self.assertEqual(md1.asDict(), md.asDict())
        md1.insert("other", "something")
        self.assertNotEqual(md1.asDict(), md.asDict())
        #-- contains
        md = MultiDict({'x': 'X', 'y': 'Y'})
        md.insert('x', 'X2')
        self.assertTrue(md.contains({'x':'X2'}))
        self.assertTrue(md.contains({'x':'X2', 'y': 'Y'}))
        self.assertFalse(md.contains({'x':'X2', 'z': 'Z'}))
        #-- __getitem__, __setitem__
        md = MultiDict({'x': 'X', 'y': 'Y'})
        self.assertEqual(md['x'], ['X'])
        md['x'] = 'A'
        self.assertEqual(md['x'], ['X', 'A'])

    def testLastNonTextNode(self):                    
        """lastNonTextNode"""
        root = GenEl('root')
        first = GenEl('first')
        second = GenEl('second')
        third = GenEl('third')
        root.addChild(first)
        first.addChild(second)
        second.addChild(third)
        self.assertEqual(root.lastNonTextNode(), third)
        third.addChild(Text('hello'))
        self.assertEqual(root.lastNonTextNode(), third)

    def testLinkNodes(self):                    
        """linkNodess"""
        root = Node()
        a = Node()
        b = Node()
        c = Node()
        l = [root, a, b, c]
        linkNodes(l)
        self.assertEqual(root.children, [a])
        self.assertEqual(a.children, [b])
        self.assertEqual(b.children, [c])
        e1 = GenEl('e1')
        e2 = GenEl('e2')
        e3 = GenEl('e3')
        e4 = GenEl('e4')
        t = Text('hello')
        linkNodes([e1, e2, e3, e4, t])
        self.assertEqual(e1.lastNonTextNode(), e4)

    def testGenEl(self):                    
        """GenEl"""
        e=GenEl('e')
        e.addAttr('k', 'v1')
        e.addAttr('k', 'v2')
        e.addAttr('l', 'x')
        self.assertEqual(e.atts.items(), [('k', ['v1', 'v2']), ('l', ['x'])])

    def testGenEl(self):                    
        """GenEl things"""
        e=GenEl() #tagless
        self.assertEqual(e.__repr__(), '<GenEl>')
        e=GenEl('tag') 
        self.assertEqual(e.__repr__(), '<tag GenEl>')
        e.atts['key'] = 'value'
        self.assertEqual(e.__repr__(), "<tag GenEl: {'key': ['value']}>")
        


