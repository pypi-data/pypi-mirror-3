.. _buml:

.. image:: logoCropped.png

buml Markup Language and Processor
===========================================================

*buml* makes it **easy** and **flexible** to **mark up** and **process
documents**.


*buml* consists of:

* a **parser** for a minimal :ref:`block-level markup language <bumlDemo>` that is

  * **configurable**, free choice of core special characters and strings

  * easily **extensible**, define additional node types (tokens)
    (e.g. support markup of some template language embedded in html)

* a fully configurable **inline parser** for

  * an easily extensible, **declaratively defined inline markup language**

* an explicit **tree of nodes** for easy post-processing and **transformations**

* **pluggable writers** to render the tree of nodes to different formats;
  currently an **xml/html writer** is supplied.


My Use Case
-------------

I wrote *buml* for my own needs where I wanted a **easy to maintain
(multi-lingual) source docment** that could be processed in different ways.
The **markup** in the source had to be minimal in order to be **unobstructive**
and let me **concentrate on content**.  

I aimed for **easy extensibility**, to **flexibly add custom behavior** for my
own markup elements.  

I also need to support **multiple output formats** and back-ends.  


Design Objectives
--------------------

*buml's* design objectives include the following:

* A :ref:`shorthand syntax <bumlDemo>` for **xml/hmtl** similar to `SHPAML
  <http://shpaml.webfactional.com/>`_, `HAML <http://haml-lang.com/>`_, `CompactXML <http://packages.python.org/compactxml/>`_.  

  * **no need to close any tags** or quotes

  * **no restrictions/quoting for text sections**: embed raw html, template
    language statements, arbitrary inline markup, anything you want

  * the special characters and separator strings of the grammar are **fully
    configurable** (but supply a reasonable default).

  * **define your own node types** with their own rendering. (Examples:
    Django/Jinja template language statements, CDATA sections, xml processing
    instructions, ..)

  * *b2x* and *bi2x* are *buml* to *xml/html* **command line converters**

* A **fully configurable inline parser** for processing text nodes.

  * **define arbitrary start and end tags** and supply a simple **handler** in
    a few lines of python code.

  * fully **recursive parsing**:  italic inside bold, replacement inside
    anchors, etc.

* Use of an **output-format independent parse tree** (tree of nodes, like in
  `ReST <http://docutils.sourceforge.net/rst.html>`_) that supports **easy
  navigation and processing** (e.g., replacement of nodes).  

  * convert xml elements to div elements identified by a class in a few lines
    of python

  * select text sections of the chosen language from a multi-language source

* **Pluggable Writers** to support multiple output formats from the same source.  


Maturity
-----------------

While this is the first release of the *buml*, the current **test suite** has a
**97% and 99% coverage** [#]_ on the block and inline **parser**, respectively.  


Why I Rolled My Own
--------------------------------

My first instinct was to use existing software to solve my problem.  In
particular, I tried  `SHPAML <http://shpaml.webfactional.com/>`_ for block
markup,  `ReST <http://docutils.sourceforge.net/rst.html>`_ for inline markup,
and `Element Tree <http://docs.python.org/library/xml.etree.elementtree.html>`_
to process the documents, implementing my own markup behavior [#]_.  

Unfortunately, I ran into several problems:

* *SHPAML* doesn't embed text in CDATA sections such that *Element Tree's* xml
  parser chokes on the inline markup I added.  SHPAML didn't seem to make it
  easy to add this in a long-term maintainable way.  

* Navigating in an Element Tree seems easy at first using XPATH (supported only
  in the most recent versions), but the `lack of the notion of "parent" <http://stackoverflow.com/questions/2170610/access-elementtree-node-parent-node>`_ of
  nodes makes it more difficult than expected.  

* Element Tree obviously supports only xml concepts.  If you want to mix in
  other types of nodes with different rendering like those *{{ used }}* in *{%
  templage languages %}* like *Django* or *Jinja*, things get more complicated
  and much of the tools like pretty printers don't work anymore.  

* ReST is extensible with you own custom markup, but the mechanisms are more
  complicated than I hoped for.  


Detailed Documentation
-----------------------

.. toctree::
   :maxdepth: 1

   A Block-Level Markup Demo <demo>
   The Block-Level Parser Architecture <architecture>
   b2x Command Line Converter <cli>
   Inline Parsing in General <inlineParsing>
   bundledInlineParser
   writerConfig
   Exploring Trees of Nodes <interactive>
   The Grammar of Block-Level Markup <bnf>

.. rubric:: footnotes

.. [#]  Use :command:`python setup.py nosetests`

.. [#]  examples for custom behavior is language selection (multiple languages
        contained in same source), language-dependent substitution, protection
        of e-mail addresses, etc. 

