The Bundled Inline Parser
--------------------------------------------

The inline parser that is bundled with *buml* is really **a generic
implementation** or maybe a **meta-parser** that only knows that tokens are
enclosed by a **start** and an **end tag**.  

Which *start* and *end tags* there actually are, and how to handle the text
between these tags is defined by an **Inline Mapper** module that provides a
**mapping specification** to the inline parser.  

The following shows the *InlineMapper* method that returns the mapping
specification:

.. code-block:: python

    def mappingSpec(self):
        "returns the mappingSpec"
        m = MappingSpec()
        #necessary Null Mapper for Text without matches:
        m.append(MappingSpecItem('', '', self.textHandler))
        m.append(MappingSpecItem('*', '*', self.emHandler))
        m.append(MappingSpecItem('**', '**', self.strongHandler))
        m.append(MappingSpecItem('[[', ']]', self.linkHandler))
        m.append(MappingSpecItem('::', '::', self.replaceHandler, 
                                 singleWord=True))

A *MappingSpec* instance is basically a list that contains *MappingSpecItems*.
Each item defines a *start* and *end tag* and a function that handles the
string between these tags.  

Using an **emtpy string** as start and end tags is a trick to specify the
handler for text without any inline markup.  Usually, that just returns a Text
Node.  

.. code-block:: python

    def textHandler(self, txt):
        return [self.nodeFactory.mkTextNode(txt)]

It then defines the inline markup for **emphasis** (between **\***), **strong**
(between **\*\***), **substitution** of single words (between **::**) and
**hyper-links** (between **[[** and **]]**).

The first three handlers simply mark up the text content with **em**,
**strong**, and **replace** elements, respectively:

.. code-block:: python

    def emHandler(self, txt):
        return self._singleElHandler(txt, 'em')

    def strongHandler(self, txt):
        return self._singleElHandler(txt, 'strong')

    def replaceHandler(self, txt):
        return self._singleElHandler(txt, 'replace', recurse=False)

The first two handlers ask for the inline parser to be applied recursively to the contained text, for example, to allow for emphasized sections inside strong sections.  The last handler is "terminal" and refrains from recursing.  

Recursion is implemented simply as follows:

.. code-block:: python

    def _singleElHandler(self, txt, elTag, elAtts=None, recurse=True):
        atts = elAtts or {}
        el = self.nodeFactory.mkElementNode(elTag, atts)
        if recurse:
            children = parse(txt, self.mappingSpec()) #recursive parsing
        else:
            children = [self.nodeFactory.mkTextNode(txt)]
        el.setChildren(children)
        return [el]

Note that it would be easy to modify this to use a different markup
specification while descending recursively.  

The link handler is different since it parses the content of the marked up
section. It expects either something like "my site <http://bruegger.it>" or
"http://bruegger.it".   It uses a utility to separate this into a *name* and an
*address*, the latter of which becomes the attribute of an *a* element:

.. code-block:: python

    def linkHandler(self, txt):
        addr, name = addrNameFromString(txt)
        attD = {'href': addr}
        return self._singleElHandler(name, 'a', elAtts=attD)


These examples and the fact that the complete inlineMapper module consists of
only 41 lines of code (without comments) shows **how easy it is to write your
own custom inline markup**.  

Since the *parse* function requires the explicit passing of the mapping
specification, it is easy to mix different choices of inline markup inside a
single document.  

.. code-block:: python

    def parse(txt, mappingSpec):

