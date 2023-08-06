from utilities import warning, addrNameFromString
from inlineParser import parse as inlineParse

try:
    import bud.nospam
except:
    pass

try:
    import nonEx
except:
    pass

#----------

def applyInlineMarkup(startNode, mappingSpec):
    "runs the inlineParser to mark up all special inline text spans"
    allTextNodes = startNode.findAllNodes('Text')
    for tn in allTextNodes:
        newChildren = inlineParse(tn.txt, mappingSpec)
        tn.replaceWith(newChildren)

def convertToDiv(startNode, nodeFactory):
    "converts elements to DIV, putting the former tag name as class attribute"
    allEls = startNode.findAllEls()
    for el in allEls:
        el.replaceWith(nodeFactory.mkElementNode('div', {'class': el.tag}))

if 'bud' in globals(): #bud.nospam import worked
    def _protectedEmail(addrStr):
        """parses address string and returns a protected string
           expected address string is either
              'user@server.domain'   or
              'full name <user@server.domain>'
        """
        addr, name = addrNameFromString(addrStr)
        return bud.nospam.js_obfuscated_mailto(addr, name)

    def protectEmailNode(elNode):
        "converts the TextNode under elNode to anti-spam format"
        assert elNode[0].__class__.__name__ == 'Text'
        elNode[0].txt = _protectedEmail(elNode[0].txt)

