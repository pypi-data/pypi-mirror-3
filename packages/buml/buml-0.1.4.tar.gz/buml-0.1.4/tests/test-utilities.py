from __future__ import absolute_import
from ..buml.utilities import *
from ..buml.transformUtils import _protectedEmail

import re

#def testNoseFindsMe():
#    "utilities: testNoseFindsMe"
#    assert 0


def test_findPatternPos():
    "utilities: findPatternPos"
    pat = re.compile("xx")
    assert findPatternPos('aasdf', pat) == -1
    assert findPatternPos('aaxxf', pat) == 2 
    assert findPatternPos('xxsdf', pat) == 0

def test_emailObfuscation():
    "transfromUtils: email protection"
    DEBUG = False
    try:
        import bud.nospam
    except:
        pass
    if not 'bud' in locals():
        print "bud.nospam is not installed"
        print 'try: "pip install bud.nospam" in order to pass test'
        assert 0
    s = 'user@domain.org'
    ss = _protectedEmail(s)
    spec = ('<script type="text/javascript">document.write(\n'
            '"<n uers=\\"znvygb:hfre\\100qbznva\\056bet\\">'
            'hfre\\100qbznva\\056bet<\\057n>".replace'
            '(/[a-zA-Z]/g, function(c){return String.fromCharCode'
            '((c<="Z"?90:122)>=(c=c.charCodeAt(0)+13)?c:c-26);})\n'
            ');\n</script>')
    print s
    ll=ss.split('\n')
    l = spec.split('\n')
    z = zip(ll, l)
    for x, y in z:
        print x
        print y
        print
    if DEBUG:
        html = "<html><body>%s</body><html>" % ss
        open('emailNoName.html','w').write(html)
    assert ss == spec

    s = 'john dipper <user@domain.org>'
    ss = _protectedEmail(s)
    spec = ('<script type="text/javascript">document.write(\n'
            '"<n uers=\\"znvygb:hfre\\100qbznva\\056bet\\">'
            'wbua qvccre<\\057n>".replace(/[a-zA-Z]/g, '
            'function(c){return String.fromCharCode'
            '((c<="Z"?90:122)>='
            '(c=c.charCodeAt(0)+13)?c:c-26);})\n'
            ');\n</script>')
    ll=ss.split('\n')
    l = spec.split('\n')
    z = zip(ll, l)
    for x, y in z:
        print x
        print y
        print
    if DEBUG:
        html = "<html><body>%s</body><html>" % ss
        open('emailWName.html','w').write(html)
    assert ss == spec

