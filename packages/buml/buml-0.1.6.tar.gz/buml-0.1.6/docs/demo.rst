.. _bumlDemo:

Demo of block-level *buml* Markup
------------------------------------

The easiest way to learning *buml* block-level markup is by example.  The
following shows all major features.  The examples show the default
configuration of special characters and separator strings.

buml Comments
^^^^^^^^^^^^^

A **/** at the start of the line marks a buml comment that isn't rendered by
writers.  

.. list-table:: 
   :widths: 45 45
   :header-rows: 1

   * - buml
     - html
   * - .. code-block:: awk

          /  any line starting with a slash is a buml comment
          // that isn't rendered
          /* by writers

     -      

xml/html Comments
^^^^^^^^^^^^^^^^^

A **!** at the start of the line marks an xml/html comment

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: awk

          ! this is an xml comment

     - .. code-block:: html

          <!-- this is an xml comment -->


xml/html Elements
^^^^^^^^^^^^^^^^^

Elements are declared by their tag name.  Parent-child relationships are
specified by the indent.  Text contained by elements starts with **"** for a
single line or **"""** for multiple lines.  **Elements are automatically
closed**.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

               html
                 body
                    h1 "Welcome to buml
                    p """This is text
                         that spans
                         multiple lines

     - .. code-block:: html

            <html>
              <body>
                <h1>Welcome to buml</h1>
                <p>
                  This is text
                  that spans
                  multiple lines
                </p>
              </body>
            </html>
      

Class Attributes
^^^^^^^^^^^^^^^^^

Like in CSS, '**.**' precedes a class attributes

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

             p.cool "This is a cool paragraph
             p.cool.blue "this has two classes


     - .. code-block:: html

                 <p class="cool">This is a cool paragraph</p>
                 <p class="cool blue">this has two classes</p>

ID Attributes
^^^^^^^^^^^^^^^

Like in CSS, '**#**' precedes an id attribute

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          div#navbar "bar here


     - .. code-block:: html

         <div id="navbar">bar here</div>

Generic Attributes
^^^^^^^^^^^^^^^^^^

**@** is used to mark generic attributes.  The attribute value is specified
after an **=** sign.  Quoting of attribute values with **single quotes** is
only necessary if the value contains a blank, a '.', or a '#' character.
Omitting the attribute value uses the default value of *True*.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 
          
             h1@myAttr=something "title 1
             h2@att2='two words' "title 2
             img@src='me.png'
             a@href='else#where "go'
             h3@flag "set to True
             h4@a1=v1@a2=v2 "two attrributes

     - .. code-block:: html

            <h1 myAttr="something">title 1</h1>
            <h2 att2="two words">title 2</h2>
            <img src="me.png"/>
            <a href="else#where">go</a>
            <h3 flag="True">set to True</h3>
            <h4 a1="v1" a2="v2">two attributes</h4>


Default Element
^^^^^^^^^^^^^^^^^^

If the element name is omitted but an element is implied by attributes, a
**div** element is set by default.  

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 
          
             .class1 "A dev element
             #id1 "this too



     - .. code-block:: html

              <div class="class1">A dev element</div>
              <div id="id1">this too</div>

Mixed and Combined
^^^^^^^^^^^^^^^^^^

Obviously, different attribute types can be mixed and combined.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 
         
              .cl1#id1@att1=v1.cl2 "all mixed

     - .. code-block:: html

              <div class="cl1 cl2" att1="v1" id="id1">all mixed</div>

Empty Element Handling
^^^^^^^^^^^^^^^^^^^^^^

Empty elements are detected **automatically**.  

Three different rendering styles are configurable:  

**sgml**
   That results in **<br>**

**xml**
   That results in **<br/>**.  This is the default.

**compat**
   That results in **<br />**

See :ref:`writerConfig` for details.  



Descending Elements in a Single Line
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to specify a chain of descending elements in a single line, using
**>** as a separator.  (Using CSS syntax)

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 
         
         ul > li > a@href='this.html' "first item
              li "second item

     - .. code-block:: html

          <ul>
            <li>
              <a href="this.html">first item</a>
            </li>
            <li>second item</li>
          </ul>

Same-level Elements in a Single Line
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to specify a group of same-level elements in a single line,
using **&** as a separator. 

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 
         
          br & br & hr & br


     - .. code-block:: html

          <br/>
          <br/>
          <hr/>
          <br/>

Mixed Same-level and Descending Elements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to mix these in a single line.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 
         
          div > img@src='me.png' & br & br & ul > li "only one item



     - .. code-block:: html

              <div>
                <img src="me.png"/>
              </div>
              <br/>
              <br/>
              <ul>
                <li>only one item</li>
              </ul>

Mixed Content
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to represent mixed content.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 
         
          p
            "this is a first line
            em "something emphasized
            " and
            strong "something strong
            "and some tail

     - .. code-block:: html

          <p>
            this is a first line
            <em>something emphasized</em>
             and
            <strong>something strong</strong>
            and some tail
          </p>

Text with Arbitrary Characters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to use any character whatsoever in text sections.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          .cooltext """asdf 0708 ~!@#$%^&*()_+`\|/?,./<>-=_+
                       and even " and """ without having to
                       close anything
  

     - .. code-block:: html


          <div class="cooltext">
            asdf 0708 ~!@#$%^&*()_+`\|/?,./<>-=_+
            and even " and """ without having to
            close anything
          </div>

Text: Empty Lines and Indentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Empty lines are possible and indentation is relative to the start of the first
line.  

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

             .indent """and empty lines:
         
                        and any kind of indentation
                          relative 
                            to 
                              the
                           start
                             of 
                        the 
                                   first
                          line
  

     - .. code-block:: html

          <div class="indent">
            and empty lines:
            
            and any kind of indentation
              relative 
                to 
                  the
               start
                 of 
            the 
                       first
              line
          </div>


Text: Embedding Raw HTML/XML
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Consequently, it is possible to embed raw html/xml in text sections.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          div """<em>evidently</em> you can
                 embedd <html></html> like
                 <a href="http://bruegger.it">visit</a>
  

     - .. code-block:: html

          <div>
            <em>evidently</em> you can
            embedd <html></html> like
            <a href="http://bruegger.it">visit</a>
          </div>
      
Text: Inline Markup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Buml lets you embed other markup languages such as ReST in text sections.

This is used with **inline parsers** that are configurable.  (coming shortly)

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          div """and you can use *inline* **markup**
                 like `reStructured Text 
                 <http://docutils.sourceforge.net/rst.htm>`_
          
                 ..topic:: Interesting
     
                    That you can pass to some
                    configurable **inline parser**

     - .. code-block:: html

            <div>
              and you can use *inline* **markup**
              like `reStructured Text 
              <http://docutils.sourceforge.net/rst.htm>`_
              
              ..topic:: Interesting
              
                 That you can pass to some
                 configurable **inline parser**
            </div>

  
Support for Template Languages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since you can embed just anything in text, any template language is supported.

Here is a Mako example.  Note that TextNodes currently cannot have children.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          table
              "<%def name="makerow(row)">
              tr 
                 "% for name in row:
                 td "${name}
                 "% endfor
              "</%def>

     - .. code-block:: html

          <table>
            <%def name="makerow(row)">
            <tr>
              % for name in row:
              <td>${name}</td>
              % endfor
            </tr>
            </%def>
          </table>

As a matter of fact, since Mako definitions behave like xml elements, and
*buml* is less restrictive of element tag names, this can even be simplified as
follows:  

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          table
              %def@name=makerow(row)
                tr 
                  "% for name in row:
                  td "${name}
                  "% endfor

     - .. code-block:: html


        <table>
          <%def name="makerow(row)">
            <tr>
              % for name in row:
              <td>${name}</td>
              % endfor
            </tr>
          </%def>
        </table>

I experimented with adding specific support for Django / Jinja syntax.  A new
line starting with **{{** or **{%** is recognized as a template statement and
is automatically closed.  


.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          {% for user in users 
             li
               a@href='{{ user.url }}'
                 {{ user.username
          {% endfor


     - .. code-block:: html


          {% for user in users %}
            <li>
              <a href="{{ user.url }}">
                {{ user.username }}
              </a>
            </li>
          {% endfor %}

*buml* makes it very easy to support any kind of additional node types by a
simple declaration of the markup in the *nodeFactory* module.  An example for
the Template Node is here:

.. code-block:: python

    #include { for templating support:
    SINGLE_LINE_TYPES = list('/!|*{')
    
    class NodeFactory:
    #...
    
        def mkSingleLineNode(self, lineStr):
             #...
             if typeChar == '{':
                return self.nodesModule.Template(tag=specStr[0], 
                                                 txt=specStr[1:].strip())

and make sure that the *writerModule* knows how to render the nodes:

.. code-block:: python

    class Template(baseNodes.GenEl, Node):
        def startTag(self):
            return '{%s ' % self.tag
    
        def endTag(self):
            if self.tag == '%':
                return ' %}'
            elif self.tag == '{':
                return ' }}'
            else:
                warning('Unknown Template Type %s for "%s"' % (self.tag, self.txt))
                #trying anyhow:
                return ' %s}' % self.tag


XML with buml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is nothing html-specific about buml and you can equally write xml. 

For better support, processing instructions are marked up by lines starting
with **?**.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          ?xml@version='1.0'@encoding=ISO-8859-1
          ?PITarget "PIContent
          ?php "echo $a;

     - .. code-block:: xml

          <?xml version="1.0" encoding="ISO-8859-1"?>
          <?PITarget PIContent ?>
          <?php echo $a; ?>



DOCTYPE, ELEMENT and ATTLIST declarations are supported by lines starting with
**|**.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

           |DOCTYPE anything here
           |ELEMENT works too
           |ATTLIST also possible

     - .. code-block:: xml

          <!DOCTYPE anything here>
          <!ELEMENT works too>
          <!ATTLIST also possible>

An example of xml that uses a name space:

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          root@xmlns:h='http://www.w3.org/TR/html4/'
           h:table
              h:tr
                h:td "first
                h:td "second


     - .. code-block:: xml

          <root xmlns:h="http://www.w3.org/TR/html4/">
            <h:table>
              <h:tr>
                <h:td>first</h:td>
                <h:td>second</h:td>
              </h:tr>
            </h:table>
          </root>
          

CDATA sections can be marked up with a **[** that behaves just like an element.

.. list-table:: 
   :widths: 45 45 
   :header-rows: 0

   * - .. code-block:: antlar 

          root
             text
                [ """this is a CDATA 
                     section and can 
                     contain any 
                     character
                     <>^&/
             ! note that no additional whitespace 
             ! is added to the text


     - .. code-block:: xml


          <root>
            <text>
              <![CDATA[this is a CDATA 
              section and can 
              contain any 
              character
              <>^&/]]>
            </text>
            <!-- note that no additional whitespace -->
            <!-- is added to the text -->
          </root>
