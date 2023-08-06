Exploring a Tree of Nodes
------------------------------------------

Python is fun since it can be used interactively.  Here is how to explore a
parse tree and learn a lot on nodes and how the parser works.  

Assume we have a file *example.buml*::

    !a comment
    html@lang=en > head > title "Welcome to buml
      body > h1 "Welcome to buml
        p.cool 
          "mixed content with a text head
          em "something emphasised
          "and a text tail
        ul > li "first
          li#i2.odd "second
          li "third

We then call *b2x* interactively::

    python -i b2x example.buml

*b2x* does the conversion and python remains at the interactive prompt *>>>*::

    bud@bud-laptop:~/wrk/CV/buml$ python -i bin/b2x testData/ex.buml 
    <!-- a comment -->
    <html lang="en">
      <head>
        <title>Welcome to buml</title>
      </head>
      <body>
        <h1>Welcome to buml</h1>
        <p class="cool">
          mixed content with a text head
          <em>something emphasised</em>
          and a text tail
        </p>
        <ul>
          <li>first</li>
          <li id="i2" class="odd">second</li>
          <li>third</li>
        </ul>
      </body>
    </html>>>> 

Let's see what we can play with:

.. code-block:: python

   >>> dir()
   ['__builtins__', '__doc__', '__name__', '__package__', 'inf', 'outf', 'parseBuml', 'rootNode', 'sys', 'usage']

Important for us is *rootNode* since it is the root of the resulting parse tree
and the object of our exploration.  We copy it to *r* to avoid typing and 
have a closer look. 

.. code-block:: python

   >>> r = rootNode
   >>> r
   <Node instance: I'm the root>

It is an instance of *Node* that all other Node classes inherit from and since
it lacks a *parent*, it *is the root*.   A root node is used in order to support documents or document snippets that lack a single root node.  

.. code-block:: python

    >>> dir(r)
    ['__doc__', '__getitem__', '__init__', ..
    'addChild',.. 'children', 'delChild', ..'findAllEls', 
    'findAllNodes', .. 'parent', 'pprint', 'txt', 'xml', ..]

For easier reading of the attributes of *r*, I eliminated some of them.

Important for the exploration are the **properties** *txt*, *children*,
and *parent*.  

The **methods** *addChild* and *delChild* were used to build the parse tree.

The **xml** method was defined in *baseWriterNodes* and is what *b2x* uses to
create *xml*.

**pprint** is a handy method to look at a whole tree (as will be demonstrated below).  

**findAllNodes** and **findAllEls** make it very easy to find certain nodes in
the tree.  

Let's start to explore some:


.. code-block:: python

    >>> r.children
    [<XmlComment>, <html Element: {'lang': ['en']}>]

*r* evidently has two children, an *XmlComment* and an *html Element*.  

Children are accessed the same way as in lists:
    
.. code-block:: python

    >>> c = r[0]
    >>> h = r[1]
    >>> c
    <XmlComment>
    >>> h
    <html Element: {'lang': ['en']}>

In the same way as nodes know about their children, they also know about their
parent.  This makes navigation in trees easy [#]_.  
    
.. code-block:: python

    >>> r
    <Node instance: I'm the root>
    >>> r.children
    [<XmlComment>, <html Element: {'lang': ['en']}>]
    >>> r[0].parent
    <Node instance: I'm the root>
    

*Leave nodes* as for example *TextNodes* or *XmlComments* have a *txt*
attribute that contains their content.  

.. code-block:: python

    >>> c.txt
    'a comment'

*Element style* nodes, i.e., nodes that inherit from *GenEl*, have empty *txt*
attributes but manage all their content in child nodes.  Textual content is
expressed in form of *TextNodes*.

.. code-block:: python

    >>> h.txt
    ''
    >>> t = h[0][0]
    >>> t
    <title Element>
    >>> t.txt
    ''
    >>> t.children
    [<Text instance: "Welcome ..">]
    >>> t[0].txt
    'Welcome to buml'

Note that the use of *TextNodes*, unlike *txt* attributes, makes "mixed
content" possible.  

.. code-block:: python

    >>> p=h[1][1]
    >>> p
    <p Element: {'class': ['cool']}>
    >>> p.children
    [<Text instance: "mixed co..">, <em Element>, <Text instance: "and a te..">]
    >>> p[1][0]         
    <Text instance: "somethin..">


*Element-style* nodes have a *tag* attribute:

.. code-block:: python

    >>> h.tag
    'html'

This is not the case for *leave nodes*, however.

.. code-block:: python

    >>> t[0]
    <Text instance: "Welcome ..">
    >>> t[0].tag
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'Text' object has no attribute 'tag'

*Element-style* nodes also have attributes.  They are of type *MultiDict* where
as single key maps to multiple values, i.e., a list of values.  The convenience
method *attDict* returns a normal dictionary.

.. code-block:: python

    >>> h
    <html Element: {'lang': ['en']}>
    >>> h.atts
    <buml.baseNodes.MultiDict object at 0xb750e8ac>
    >>> h.attDict()
    {'lang': ['en']}
    >>> h.atts['lang']
    ['en']

For a quick overview of a complete tree or subtree, use the *pprint* method. 

.. code-block:: python

    >>> r.pprint()
    [ <Node instance: I'm the root>,
      [ <XmlComment>,
        [ <html Element: {'lang': ['en']}>,
          [ [ <head Element>,
              [[<title Element>, [<Text instance: "Welcome ..">]]]],
            [ <body Element>,
              [ [<h1 Element>, [<Text instance: "Welcome ..">]],
                [ <p Element: {'class': ['cool']}>,
                  [ <Text instance: "mixed co..">,
                    [<em Element>, [<Text instance: "somethin..">]],
                    <Text instance: "and a te..">]],
                [ <ul Element>,
                  [ [<li Element>, [<Text instance: "first">]],
                    [ <li Element: {'id': ['i2'], 'class': ['odd']}>,
                      [<Text instance: "second">]],
                    [<li Element>, [<Text instance: "third">]]]]]]]]]]

And for quickly finding nodes of a certain type, use the *findAllNodes* method
with the node type as argument

.. code-block:: python

    >>> r.findAllNodes('XmlComment')
    [<XmlComment>]
    >>> from pprint import pprint
    >>> pprint(r.findAllNodes('Text'))
    [<Text instance: "Welcome ..">,
     <Text instance: "Welcome ..">,
     <Text instance: "mixed co..">,
     <Text instance: "somethin..">,
     <Text instance: "and a te..">,
     <Text instance: "first">,
     <Text instance: "second">,
     <Text instance: "third">]

For *element-style* nodes, the method *findAllEls* that can search on the *tag*
and on attributes is available.  

All *Elements*:

.. code-block:: python

    >>> pprint(r.findAllEls())
    [<html Element: {'lang': ['en']}>,
     <head Element>,
     <title Element>,
     <body Element>,
     <h1 Element>,
     <p Element: {'class': ['cool']}>,
     <em Element>,
     <ul Element>,
     <li Element>,
     <li Element: {'id': ['i2'], 'class': ['odd']}>,
     <li Element>]

Filtering on the kind of tags:

.. code-block:: python

    >>> pprint(r.findAllEls(tagVals=['head', 'body']))
    [<head Element>, <body Element>]

Filtering on attributes:

.. code-block:: python

   >>> pprint(r.findAllEls(attVals={'class': 'cool'}))
   [<p Element: {'class': ['cool']}>]



.. rubric:: footnotes

.. [#] Note that ElementTree `lacks of the notion of "parent" 
       <http://stackoverflow.com/questions/2170610/access-elementtree-node-parent-node>`_
