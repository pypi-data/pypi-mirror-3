from docutils.examples import html_body

def rst(rstStr):
    "ReST parser from docutils"
    rendered = html_body(rstStr, input_encoding='utf-8', 
                         output_encoding='utf-8').strip()
    if rendered.startswith('<div class="document">\n'):
        rendered = rendered[23:]
        if rendered.endswith('\n</div>'):
            rendered = rendered[:-7]
    #alternative: find first > and last < and cut off there...
    return rendered
