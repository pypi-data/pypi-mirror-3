*b2x* and *bi2x* Command Line Converters
------------------------------------------

**b2x** and **bi2x** are command line converters from *buml* to *xml*.  

**b2x**
    applies solely the **block-level** parser and produces **pretty printed
    xml** output

**bi2x**
    applies both the **block-level** and the **inline parser** and produces xml
    **without additional whitespace**

they can both read either from *stdin* or from a file and write to *stdout* or
a file.  

From File to File
^^^^^^^^^^^^^^^^^^^^^

Converting *demo.buml* to *demo.xhtml*::

    b2x demo.buml demo.xhtml
    bi2x demo.buml demo.xhtml

From File to STDOUT
^^^^^^^^^^^^^^^^^^^^

Printing the conversion of *demo.buml* to *stdout*::

    b2x demo.buml 
    bi2x demo.buml 


From STDIN to STDOUT
^^^^^^^^^^^^^^^^^^^^^

Using *b2x* as a Unix filter::

    b2x
    bi2x



Using b2x inside the *vim* Editor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some text editor support the use of Unix filters, i.e., programs that read
input from *stdin* and write to *stdout*.  An example is *vim*.  

In *vim*, select a range of lines that contains *buml* source (using *V* and
cursor movement keys).  Then type [#]_ ::

    !b2x  
    !bi2x
    
and *whoops* the *buml* is replaces by *xml*.  


.. [#] This assumes that *b2x* is in you path.  If not, give a complete
       absolute or relative path to *b2x*, as for example *./b2x* if it is in
       the same directory.    
  
