The *buml* block-level parser Architecture
-------------------------------------------


.. sidebar:: buml Architecture
   
   The following figure illustrates
   the buml architecture:

   .. image:: buml.png

b2x calls the block Parser
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The main component that gets the actual work done is **b2x**, the command-line
*buml* to *xml* converter.  Other applications may use different converters or
transformers, all of which take the same architectural role.  

*b2x* calls *parseBuml* from the parser module *bumlParse.py*, passing a *buml*
formatted string as argument.  

*parseBuml* returns the **root node** of the parse tree it has constructed based on the *buml* source string.  

Parser uses nodeFactory
^^^^^^^^^^^^^^^^^^^^^^^^

The *parser* is solely concerned with the syntactic analysis of the *buml*
source.  Once it has tokenized the source string, it relies on the
*nodeFactory* to create the corresponding nodes.  

The *nodeFactory* uses token names to make decisions about the mapping to
nodes.  For example, token names starting with a *!* are currently mapped to
*XmlComment* nodes; token names starting with normal letters are mapped to xml
*Element* nodes.  

The *nodeFactory* is thus a natural point for modifications and extensions.
The supplied nodeFactory has less than 50 lines of code and is thus easy to
modify or (better) substitute.  

The nodeFactory instantiates writerNodes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The *nodeFactory* imports the module that defines the nodes it
instantiates.  It thus selects the *writer* functionality that
will be available in node methods.  

In the default configuration, *nodeFactory* uses the node classes defined in
*baseWriterNodes*.  These nodes know how to render themselves to *xml/html*.

To add different rendering methods (such as *pdf* or *docBook*) or use a
different writer module, just import a different writer module in
*nodeFactory*.  It is possible to use the classes of baseWriterNodes as mixins.  

WriterNodes extend baseNodes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The *baseWriterNodes* module does not need to implement nodes from scratch.
Much rather, it extends the *baseNode* module that provides nodes with all the
base functionality needed by the *parser* to build and navigate the *parse
trees* and by transformers to modify it.  

The *writer* module also determines which node classes are available to the
*nodeFactory* and thus the *parser*.  *BaseWriterNodes*, based on the only tree
classes of *baseNodes*, defines nine different node classes, including *CDATA*
and *Template* whose rendering methods differ, e.g., from those of xml element
nodes.  Adding new node classes is often as easy as inheritance and
over-writing the *startTag* and *endTag* method.  

Note that *writers* and *transformers* are not limited to producing rendering
formats.  They could for example also create an ElementTree or an ReST parse
tree to combine the functionality of buml with that of some consolidated other
package.  

Show me the Code
^^^^^^^^^^^^^^^^

The dependence of the various modules in the architecture are evident when
looking at an explicit way of building and using a parser instance:


.. code-block:: python

    >>> from buml import baseWriterNodes
    >>> from buml.nodeFactory import NodeFactory
    >>> from buml.bumlParser import Parser
    >>>
    >>> nodeFact = NodeFactory(baseWriterNodes)
    >>> parser = Parser(nodeFact)
    >>> buml = '.cool "A cool div element'
    >>> rootNode = parser.parseBuml(buml)
    >>> print rootNode.xml()
    <div class="cool">A cool div element</div>
    




