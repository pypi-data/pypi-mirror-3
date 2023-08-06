Backus–Naur Grammar for buml's Block-Level Parser
--------------------------------------------------

*buml's* block parser has a minimum of syntax hard-coded.  We call that **core
buml**.  It puts the *minimum restrictions* on the choice of possible tokens
possible.  

Within these restrictions, the **nodeFactory** module usually introduces
**additional syntax** to identify **special characters** which, put at the
beginning of a line, identify simple elements.  

A key concept of *buml* is that **indentation** specifies the **hierarchical
relationship** of language tokens that is then used to build a hierarchical parse
tree.  This concept is intuitively easy to understand.  

In the following, the *buml* **grammar of a single line** is described.  The
description is given in a syntax close to **EBNF**.  

Note that the **restrictions of legal characters** that can be used **in
different tokens** often goes **beyond practical relevance**; often legal *buml*
tokens would not translate to legal *xml* tokens and/or would be very
obfuscated and difficult to read.  

For simplicity, **continuations of multi-line text is excluded** from the
description.  

The following is a description of buml core syntax in EBNF syntax:

core buml
^^^^^^^^^

A *buml* document consists of multiple lines.  Lines can be either empty or specify a node::

    line = emptyLine | nodeSpec ;
    emptyLine == any white space

Two kinds of nodes exist:  simple and complex Elements::

    nodeSpec = simpleEl | complexEl ;

The former, while they still might have children, are rendered on a single
line.  This includes their *end tag*.  

Complex Elements, in the general case, enclose their children between a *start* and an *end tag*.

An example for a simple element (defined by the default nodeFactory) is an *xml
comment* [#]_ ::

    ! this is an example xml comment

It is defined by a special character at the start of the line which identifies
the simple element, and a text that follows ::

    simpleEl = specialChar , lineText ;
    specialChar == any character but "
    lineText == arbitrary series of characters except "

Which simple elements exist and what special characters identify them is exclusively defined in the *nodeFactory*. An extract of the default *nodeFactory*:

.. code-block:: python

    SINGLE_LINE_TYPES = list('/!|*')

    def isSingleLineNode(lineTypeChar):
        return lineTypeChar in SINGLE_LINE_TYPES


An example for a full-fledged complex element is the following ::

    a@href='xx' > img@src='xx' & ul > li "some text

The components of a complex element are defined in the following EBNF statement::

    complexEl = [sameLevelGroup] , { "&", sameLevelGroup}, [ TextStartMarker, Text] ;
    TextStartMarker = '"' | '"""' ;
    Text == string containing arbitrary characters without restriction

The optional text section is present::

    "some text

and starts with the **"** as TextStartMarker followed by arbitrary text.

The example shows two *sameLevelGroups*, ::

    a@href='xx' > img@src='xx' 

and ::
    
    ul > li

that are separated by an **&**.  

*sameLevelGroups* can consist of a single element or a series of descending elements: :: 

    sameLevelGroup = elSpec , { ">" , elSpec } ;

In our case, the second *sameLevelGroup* contains two elements *ul* and *li* separated by an **>**.

An element specification consists of an element name and a specification of
attributes.  If the element name is provided, the attributes are optional;
evidently, if the element name is omitted (implying a *div* element), at least
one attribute has to be present.  ::

    elSpec = elName , {attrSpec}    |    [ elName ] , attrSpec , {attrSpec} ;

    elName == any string that doesn't contain " & > . # @ 
              nor any specialChar defined by the nodeFactory

There are three types of attribute specifications: ::

    attSpec = classAtt | idAtt | genAtt ;

A *class* attribute can be specified starting with a **.** as follows: ::

    classAtt = "." , UnQuotedAttVal ;
    unQuotedAttVal == any string that doesn't contain " & > . # @

For example: ::

    div.oceanStyle

An *id* attribute is specified starting with a **#** as follows: ::

    idAtt = "#" , unQuotedAttVal ;

For example: ::

    div.navbar

A generic attribute is specified as follows: ::

    genAtt = "@" , attName, [ "=", attVal ] ;
    attName == any string that doesn't contain " & > . # @ =

For example, a *div* with two attributes is: ::

    div@att1=val1@att2='user@gmail.com'

Attribute values can optionally be quoted with single quotes: ::

    attVal = unQuotedAttVal | quotedAttVal ;
    unQuotedAttVal == any string that doesn't contain " & > . # @ 
    quotedAttVal = "'" , quotedVal , "'" ;
    quotedVal == any string that doesn't contain " & > '  

Summary of buml grammar in EBNF
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here the EBNF definition in one place: 

.. code-block:: antlr

    line = emptyLine | nodeSpec ;
    emptyLine == <any white space>
    nodeSpec = simpleEl | complexEl ;
    simpleEl = specialChar , lineText ;
    specialChar == any character but "
    lineText == arbitrary series of characters except " 
    complexEl = [sameLevelGroup] , { "&", sameLevelGroup}, [ TextStartMarker, Text] ;
    TextStartMarker = '"' | '"""' ;
    Text == string containing arbitrary characters without restriction
    sameLevelGroup = elSpec , { ">" , elSpec } ;
    elSpec = elName , {attrSpec}    |    [ elName ] , attrSpec , {attrSpec} ;
    elName == any string that doesn't contain " & > . # @ 
              nor any specialChar defined by the nodeFactory
    attSpec = classAtt | idAtt | genAtt ;
    classAtt = "." , UnQuotedAttVal ;
    unQuotedAttVal == any string that doesn't contain " & > . # @
    idAtt = "#" , unQuotedAttVal ;
    genAtt = "@" , attName, [ "=", attVal ] ;
    attName == any string that doesn't contain " & > . # @ =
    attVal = unQuotedAttVal | quotedAttVal ;
    unQuotedAttVal == any string that doesn't contain " & > . # @
    quotedAttVal = "'" , quotedVal , "'" ;
    quotedVal == any string that doesn't contain " & > '  


.. rubric:: footnotes

.. [#]  In the default nodeFactory, comments are restricted to a single line
        and it is not possible to "comment out" xml elements.
