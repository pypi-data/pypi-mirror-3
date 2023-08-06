.. _writerConfig:

Writer Configuration
---------------------------

The *baseWriterNodes* module permits to configure several rendering options:

Empty Element Rendering Mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> from bumlParser import Parser
    >>> p=Parser()
    >>> rootNode = p.parseBuml('br')
    >>> rootNode.setEmptyElementMode()   
    Warning: mode must be one of ['xml', 'sgml', 'compat']
    >>> rootNode.setEmptyElementMode('xml')
    >>> print rootNode.xml()
    <br/>
    >>> rootNode.setEmptyElementMode('sgml')
    >>> print rootNode.xml()
    <br>
    >>> rootNode.setEmptyElementMode('compat')
    >>> print rootNode.xml()
    <br />
    

Pretty or Compact Rendering
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The *baseWriterNodes* module supports two basic rendering modes, *pretty* and *noWhiteSpace*.

.. code-block:: python

    >>> buml = 'html > header > title "hello\n  body > h1 "hello\n    p "something'
    >>> print buml
    html > header > title "hello
      body > h1 "hello
        p "something
    >>> rootNode = p.parseBuml(buml)
    >>> rootNode.setRenderMode()
    Warning: mode must be one of ['pretty', 'noWhiteSpace']

The *pretty* mode indents the elements, inserting white space:

.. code-block:: python

    >>> rootNode.setRenderMode('pretty')
    >>> print rootNode.xml()
    <html>
        <header>
            <title>hello</title>
        </header>
        <body>
            <h1>hello</h1>
            <p>something</p>
        </body>
    </html>

A second argument sets the indentWidth:

.. code-block:: python

    >>> rootNode.setRenderMode('pretty', 2)
    >>> print rootNode.xml()
    <html>
      <header>
        <title>hello</title>
      </header>
      <body>
        <h1>hello</h1>
        <p>something</p>
      </body>
    </html>

For some applications, it is better to have a compact representation without additional white space:

.. code-block:: python

    >>> rootNode.setRenderMode('noWhiteSpace')
    >>> print rootNode.xml()
    <html><header><title>hello</title></header><body><h1>hello</h1><p>something</p></body></html>


Maximal Single Line Length
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For relatively short text contents, *buml* displays start, end tag and content
on a single line.  When the text content exceeds the maximal length, the tags
and content are all rendered on separate lines.  

The *setMaxSingleLineLen* method of Nodes is used to configure the threshold:

.. code-block:: python

          >>> s="""\   
          ... div "this is short
          ... div "this is a bit longer
          ... div "this is MMUUCCHH lloonnggeerr"""
          >>> rootNode = p.parseBuml(s)
          >>> rootNode.setMaxSingleLineLen(22)
          >>> print rootNode.xml()      
          <div>this is short</div>
          <div>this is a bit longer</div>
          <div>
            this is MMUUCCHH lloonnggeerr
          </div>


With a threshold of 22, only the first two *div* elements are displayed on a
single line.  Lowering the threshold, only the first line fits on a single line:

.. code-block:: python

          >>> rootNode.setMaxSingleLineLen(16)
          >>> print rootNode.xml()
          <div>this is short</div>
          <div>
            this is a bit longer
          </div>
          <div>
            this is MMUUCCHH lloonnggeerr
          </div>

