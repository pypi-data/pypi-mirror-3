from __future__ import absolute_import
from ..buml.inlineMapper import *


#def testNoseFindsMe():
#    "inlineMapper: testNoseFindsMe"
#    assert 0

def test_all():
    "inlineMapper: all"
    #just to exercise some code
    im = InlineMapper()
    assert len(im.mappingSpec()) == 5

def test_handlers():
    "inlineMapper: handlers"
    im = InlineMapper()
    t = im.textHandler('hello')
    assert t[0].__class__.__name__ == 'Text'
    assert t[0].txt == 'hello'
    em = im.emHandler('important')
    assert em[0].__class__.__name__ == 'Element'
    assert em[0].tag == 'em'
    assert em[0][0].__class__.__name__ == 'Text'
    assert em[0][0].txt == 'important'
    lnk = im.linkHandler('some name <http://bruegger.it>')
    assert lnk[0].__class__.__name__ == 'Element'
    assert lnk[0].tag == 'a'
    assert lnk[0].atts['href'] == ['http://bruegger.it']
    assert lnk[0][0].__class__.__name__ == 'Text'
    print '"%s"' % lnk[0][0].txt
    assert lnk[0][0].txt == 'some name'

