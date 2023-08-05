try:
    import urllib.request, urllib.parse, urllib.error # Python >=3.0
except ImportError:
    import urllib # Python <3.0

def print_form_javascript(filter_count, filters_data):
    """Prints out the javascript code that makes adding and removing filters
    dynamically work. It works by using jQuery Dynamic Form plugin
    (http://code.google.com/p/jquery-dynamic-form/).
    The filters are parsed from the CGI query and then to this function
    in JSON format as 'filters_data' parameter.

    Parameters:
        filter_count: maximum number of filters

        filters_data: existing filters in JSON format
        The format is as follows:
        [{"filterby":<FILTER_VARIABLE>, "filtersymbol":<FILTER_SYMBOL>, "threshold":<FILTER_THRESHOLD>}]

        Example:
        [{"filterby":"GPDISIM", "filtersymbol":">", "threshold":"10"},
         {"filterby":"GPDISIM_diff", "filtersymbol":">", "threshold":"0"},
         {"filterby":"zscore", "filtersymbol":">", "threshold":"1.8"},
         {"filterby":"zscore", "filtersymbol":"<", "threshold":"5"},]
    """
    print("""<script type="text/javascript">
    $(document).ready(function() {
        $("#filter").dynamicForm("#add_filter", "#remove_filter",
        {
            limit:%d,
            normalizeFullForm:false,
            data:%s
        });
    });
</script>""" % (filter_count, filters_data))

def print_headers(title, filter_count=20, filters_data=""):
    """Prints the headers of the html document (<head> and the beginning
    of <body>). Prints the page header.

    Parameters:
        title: page title and header
        filter_count & filters_data: see function print_form_javascript()
    """
    print("Content-Type: text/html")     # HTML is following
    print("")                            # blank line, end of headers
    print("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="http://www.cis.hut.fi/style/2005/cis.css"/>
  <link rel="stylesheet" type="text/css" href="tigreBrowser.css"/>
  <script type="text/javascript" src="jquery-1.4.2.min.js"></script>
  <script type="text/javascript" src="jquery-dynamic-form.js"></script>
  <script type="text/javascript" src="tigreBrowser.js"></script>
  """ % title)
    print_form_javascript(filter_count, filters_data)
    print("""</head>
<body>
<a href="tigreBrowser.cgi"><h1>%s</h1></a>""" % title)

def print_footer():
    """Prints the footer of the html document (</body> and </html>)
    """
    print("""</body>
</html>""")

def print_select(formdata, key, values, default=None):
    print("""<SELECT name="%s" id="%s">""" % (key, key))
    if key in formdata:
        for k in values:
            if formdata.getvalue(key) == k:
                print("<OPTION selected>%s</OPTION>" % k)
            else:
                print("<OPTION>%s</OPTION>" % k)
    else:
        for k in values:
            if default == k:
                print("<OPTION selected>%s</OPTION>" % k)
            else:
                print("<OPTION>%s</OPTION>" % k)
    print("""</SELECT>""")

def print_checkbox(formdata, key, clicked=False):
    if key in formdata or clicked:
        print("""<INPUT type="checkbox" name="%s" id="%s" checked value="yes"/>""" % (key, key))
    else:
        print("""<INPUT type="checkbox" name="%s" id="%s" value="yes"/>""" % (key, key))

def print_radiobutton(formdata, key, value, default=False):
    if key in formdata and formdata.getvalue(key) == value or (default and not formdata.getvalue(key)):
        print("""<INPUT type="radio" name="%s" checked value="%s"/>""" % (key, value))
    else:
        print("""<INPUT type="radio" name="%s" value="%s"/>""" % (key, value))

def print_input(formdata, key, default, size="4"):
    if key in formdata:
        print("""<INPUT type="text" name="%s" value="%s" size="%s"/>""" % (key, formdata.getvalue(key), str(size)))
    else:
        print("""<INPUT type="text" name="%s" value="%s" size="%s"/>""" % (key, default, str(size)))

def print_genes(genes):
    """Prints gene names as tables.
    """
    print("""<table class="stats"><tr><td>""")
    for gene in genes:
        print(gene + "<br/>")
    print("</td><td>")
    print("{")
    genes = ["'" + gene + "'" for gene in genes]
    genes = ',<br/>'.join(genes)
    print(genes)
    print("};")
    print("</td></tr></table>")

def print_pages(number, active, req, script, pagesize):
    if number < 1:
        return
    req.pop('offset', None)
    script = script or ""
    display_count = 10

    try:
        url = script + '?' + urllib.parse.urlencode(req, True) # Python >=3.0
    except AttributeError:
        url = script + '?' + urllib.urlencode(req, True) # Python <3.0

    def print_link(offset, name):
        print("""<a href="%s">%s</a>""" % (url + '&offset=' + str(offset), name))

    print("<p>Pages: ")

    # Previous
    if active > 0:
        print_link((active - 1) * pagesize, "Previous")
    elif number > 1:
        print("<strong>Previous</strong> ")

    if active > display_count - 1:
        for k in range(0, display_count // 2):
            print_link(k * pagesize, k + 1)
        min = display_count // 2
        max = active - display_count + 2
        print_link(int(pagesize * (min + max) // 2), "...")

    for k in range(number):
        if abs(active - k) < display_count:
            if k == active:
                print("<strong>%d</strong> " % (k+1))
            else:
                print_link(k * pagesize, k + 1)

    if active < number - display_count:
        min = active + display_count
        max = number - display_count // 2 + 1
        print_link(int(pagesize * (min + max) // 2), "...")
        for k in range(number - display_count // 2, number):
            print_link(k * pagesize, k + 1)

    # Next
    if active < (number - 1):
        print_link((active + 1) * pagesize, "Next")
    elif number > 1:
        print("<strong>Next</strong>")

    print("</p>")

def print_dict_table(dict):
    keys = list(dict.keys())
    keys.sort()
    print("""<table class="stats">""")
    for k in keys:
        print("<tr>")
        value = dict[k]
        if isinstance(value, list):
            value = ', '.join(value)
        print("<td>%s:</td><td>%.2f</td>" % (k.replace("_", ' '), value))
        print("</tr>")
    print("</table>")

def print_alias_dict(dict):
    keys = list(dict.keys())
    keys.sort()
    print("""<table class="stats">""")
    for alias_class in keys:
        print("""<tr class="alias_annotation_%s">""" % alias_class)
        alias = dict[alias_class]
        if alias == [None]:
            alias = 'N/A'
        if isinstance(alias, list):
            alias = ', '.join(alias)
        print("<td>%s</td><td>%s</td>" % (alias_class, alias))
        print("</tr>")
    print("</table>")

def print_figure_cell(figure, alt='', class_attr=''):
    print("""<td class="%s">""" % class_attr)
    print("<a href=%s>" % figure)
    print("""<img src="%s" width=400 height=300 alt="%s">""" % (figure, alt))
    print("</a>")
    print("</td>")

def print_highlights_table(colors, centered=False):
    if not colors:
        return
    margin = centered and "auto" or "none"
    print("""<table class="color_table" style="margin-left:%s; margin-right:auto">""" % margin)
    print("<tr>")
    for color in colors:
        print("""<td class="color" width=10 height=10 bgcolor="#%s"></td>""" % (color))
    print("</tr>")
    print("</table>")


