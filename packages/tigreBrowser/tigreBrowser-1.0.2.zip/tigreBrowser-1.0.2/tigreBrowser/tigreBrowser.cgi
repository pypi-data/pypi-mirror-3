#! /usr/bin/env python

import cgi
import cgitb; cgitb.enable()
import os
import math
import time
import sys
import platform
from tigreBrowser import results
from tigreBrowser.browser_utils import *
from tigreBrowser.database import *
from string import Template

try: # Python >=3.0
    import urllib.request, urllib.parse, urllib.error
    from configparser import RawConfigParser
except ImportError: # Python <3.0
    import urllib
    from ConfigParser import RawConfigParser

# Change the CWD to find the config file from the correct directory
os.chdir(sys.path[0])

def print_form_dataset_selection(formdata):
    """Prints dataset selection part of the form.
    Prints either 'TF' or 'Target set' selection depending on whether the
    browser is in 'Target ranking' or 'Regulator ranking' mode.
    """
    print("<fieldset>")
    print("<legend>Dataset selection</legend>")
    print("""<p><label for="experiment_set">Experiment set:</label><br/>""")
    print_select(formdata, 'experiment_set', [name for (name, id, parent) in EXPERIMENT_SETS])
    print("</p>")

    if RANKING_TYPE == TARGET_RANKING:
        print("""<p><label for="tf">TF:</label><br/>""")
        print_select(formdata, 'tf', TFs)
        print("</p>")
    else:
        print("""<p><label for="target_set">Target set:</label><br/>""")
        target_genes = db.get_gene_probe_names_dict(TARGET_SETS.values())
        print_select(formdata, 'target_set', target_genes.values())
        print("</p>")

    print("""<p><label for="numgenes">Number of genes per page:</label><br/>""")
    print_select(formdata, 'numgenes', NUMBERS, '50')
    print("</p>")

    print("""<p><label for="sort_type">Sort by:</label><br/>""")
    print_select(formdata, 'sort_type', SORT_TYPES)
    print("</p>")

    print("""<INPUT type="hidden" name="offset" value="0">""")
    print("""<p class="submit"><input type="submit" value="Send"/><input type="reset"/></p>""")
    print("</fieldset>")

def print_form_filtering(formdata):
    """Prints filtering section of the form.
    """
    print("<fieldset>")
    print("<legend>Filtering</legend>")
    print("""<p><label for="apply_filter">""")
    print_checkbox(formdata, 'apply_filter')
    print("""Apply filters</label></p><br/>""")
    print_filter_jquery(formdata)
    print("</fieldset>")

def print_form_highlight_options(formdata):
    """Prints highlight selection section of the form.
    """
    print("<fieldset>")
    print("<legend>Highlighting</legend>")
    print_supplementary_options(formdata)
    print("</fieldset>")

def print_form_search(formdata):
    """Prints search section of the form.
    """
    print("<fieldset>")
    print("<legend>Search</legend>")
    print("""<p>Search for specific genes<br/>(for example: "twi, FBgn0011656, FBgn0045759"):</p>""")
    print_input(formdata, 'search_query', '', 30)
    print("</fieldset>")

def print_form_output_options(formdata, results):
    """Prints output options section of the form.
    """
    print("<fieldset>")
    print("<legend>Output options</legend>")
    print("""<div class="option_box">""")
    print_checkbox(formdata, 'show_parameters')
    print("Show parameters</div>")
    print("""<div class="option_box">""")
    print_checkbox(formdata, 'show_genelist')
    print("Print gene name list</div>")

    if results:
        print("""<div class="option_box">""")
        print("Show following aliases:")
        print_displayed_aliases_table(formdata, results)
        print("</div>")

        print("""<div class="option_box">""")
        print("Display following figures:")
        print_displayed_figures_table(formdata, results)
        print("</div>")

    print("</fieldset>")

def print_form(formdata, results=None):
    """Prints the form.
    """
    print("""<div id="form">""")
    print('<form action="' + SCRIPT_URI + '" method="get">')

    print("""<div id="form_sort">""")
    print_form_dataset_selection(formdata)
    print("</div>")

    print("""<div id="form_filter">""")
    print_form_filtering(formdata)
    print("</div>")

    if SUPP_ANNOTATIONS:
        print("""<div id="form_highlight">""")
        print_form_highlight_options(formdata)
        print("</div>")

    print("""<div id="form_search">""")
    print_form_search(formdata)
    print("</div>")

    print("""<div id="form_output">""")
    print_form_output_options(formdata, results)
    print("</div>")

    print("</form>")
    print("</div>")

def get_filters_data(formdata):
    """Reads the CGI query string and parses the filters from it.
    Returns filters in JSON format and filters as a dictionary.

    Returns: (filters in JSON, {filterby, [symbol, threshold value]})

    Example of JSON format string:
        [{"filterby":"GPDISIM", "filtersymbol":">", "threshold":"0"},
         {"filterby":"GPDISIM_diff", "filtersymbol":">", "threshold":"0"},
         {"filterby":"zscore", "filtersymbol":">", "threshold":"1.8"},]

    Example of dictionary:
        {'GPDISIM_diff': [('>', 0.0)], 'GPDISIM': [('>', 0.0), ('<', 10.0)], 'zscore': [('>', 1.8), ('<', 6.0)]}
    """
    filters = {}
    s = ""
    for n in range(0, MAX_FILTER_COUNT):
        f = lambda x: 'filter[filter][' + str(n) + '][' + x + ']'
        key = f('filterby')
        if key not in formdata:
            continue
        filterby = formdata.getvalue(f('filterby'))
        filtersymbol = formdata.getvalue(f('filtersymbol'))
        threshold = formdata.getvalue(f('threshold'))
        if threshold != None:
            s += """{"filterby":"%s", "filtersymbol":"%s", "threshold":"%s"},""" % (filterby, filtersymbol, threshold)
            if filterby not in filters:
                filters[filterby] = []
            try:
                filters[filterby].append((filtersymbol, float(threshold)))
            except ValueError:
                pass
    return "[" + s + "]", filters

def print_filter_jquery(formdata):
    """Prints the first filter entry. The jQuery Dynamic Form plugin
    will add the rest of the filter entries.
    Prints out links to add or remove filter entries (the implementation is
    done by the forementioned plugin).
    """
    print("""<p id="filter">""")
    print_select(formdata, 'filterby', FILTER_TYPES)
    print_select(formdata, 'filtersymbol', FILTER_SYMBOLS)
    print_input(formdata, 'threshold', '')
    print("""<a href="" id="remove_filter">[-]</a>""")
    print("""<a href="" id="add_filter">[+]</a>""")

def print_supplementary_options(formdata):
    """Prints radiobuttons etc. for supplementary options.
    """
    for (type, name, desc) in SUPP_ANNOTATIONS:
        print("""<div class="option_box">""")
        print("<table>")
        print("<tr>")
        print("<td>")
        print_highlights_table([SUPP_ANNOTATION_COLORS[name]])
        print("</td>")
        print("<td>")
        print("<label>" + desc + "</label>")
        print("</td>")
        print("</tr>")
        print("</table>")
        if type == 0: # boolean
            print("yes:")
            print_radiobutton(formdata, name, "1.0")
            print("no:")
            print_radiobutton(formdata, name, "0.0")
            print("neither:")
            print_radiobutton(formdata, name, "", True)
        elif type == 1: # int
            print_select(formdata, name + '_filtersymbol', FILTER_SYMBOLS)
            print_input(formdata, name, '')
        elif type == 2: # boolean
            print_select(formdata, name + '_filtersymbol', FILTER_SYMBOLS)
            print_input(formdata, name, '')
        else:
            print("<b>Invalid supplementary data type</b><br/>")
        print("</div>")

def print_displayed_figures_table(formdata, results):
    """Prints a list of figures that can be displayed in the results listing
    and checkboxes to toggle the display status of each figure (see
    tigreBrowser.js for the implementation of showing and hiding of figures).

    Parameters:
        results: Results object
    """
    dataset_figure = results.get_dataset_figure()
    experiment_figures = results.get_experiment_figures()
    if dataset_figure:
        print("""<div>""")
        print_checkbox(formdata, 'show_dataset_figure', True)
        print("""Dataset figure</div>""")

    for (fig_id, fig_filename, fig_name, fig_desc, fig_priority) in experiment_figures:
        print("""<div>""")
        print_checkbox(formdata, 'show_experiment_figure_' + str(fig_id), True)
        print("""%s</div>""" % fig_name)

def print_displayed_aliases_table(formdata, results):
    """Prints a list of aliases that can be displayed in the results listing
    and checkboxes to toggle the display status of each alias (see
    tigreBrowser.js for the implementation of showing and hiding of figures).

    Parameters:
        results: Results object
    """
    annotations = results.get_alias_annotations()
    for (alias_id, alias_class, alias_source, alias_desc) in annotations:
        print("<div>")
        show = alias_class == 'GENENAME' # show GENENAME aliases by default
        print_checkbox(formdata, 'show_alias_annotation_' + str(alias_class), show)
        print("%s</div>" % alias_class)

def template_to_figure_string(template, name):
    """Converts the given template figure string to a real string by
    substituting ${probe_name} with the given name.
    """
    if not template:
        return ''
    t = Template(template)
    return t.substitute(probe_name = name)

def print_result(results, zscore, supps, probe_name, dataset_figure, experiment_figures, gene_id):
    """Prints experiment results and figures for the given gene id.

    Parameters:
        results: Results object
        zscore: z-score for this gene
        supps: dictionary of supplementary data for this gene: {supplementary dataset name: value}
        probe_name: probe name for the gene
        dataset_figure: template string for the dataset figure
        experiment_figures: list of experiment figure annotations [(figure id, filename, name, description, priority)]
        gene_id: gene id
    """
    if dataset_figure is not None and dataset_figure != '':
        fig_exp = template_to_figure_string(dataset_figure, probe_name)
        print_figure_cell(fig_exp, probe_name, 'figure_dataset')
    print("<td nowrap>")
    print("""<div class="result_box">""")
    print_dict_table(results)
    if zscore != None:
        print("""</div><div class="result_box">""")
        print_dict_table({"z-score": zscore})
    print("""</div><div class="result_box">""")
    print_dict_table(supps)
    print("</div>")
    print("</td>")
    for (fig_id, fig_filename, fig_name, fig_description, fig_priority) in experiment_figures:
        if fig_filename:
            t = template_to_figure_string(fig_filename, probe_name)
            print_figure_cell(t, '', 'figure_experiment_' + str(fig_id))
        else:
            print_figure_cell(SCRIPT_URI + '?show_figure=1&figure_id=%d&gene_id=%d' % (fig_id, gene_id), '', 'figure_experiment_' + str(fig_id))

def print_highlights(gene_id, highlights, color_names):
    """Prints highlight boxes for the given gene id.

    Parameters:
        gene_id: gene id to highlight
        highlights: dictionary mapping of supplementary dataset names to
                    gene ids to be highlighted:
                    {supp dataset name: [gene ids]}
                    Example: {'ischip': [4632, 8354, 10609], 'isinsitu': [], 'hasinsitu': [4632, 8354, 10609]}
        color_names: dictionary mapping of supplementary dataset names to
                     hex color codes: {supp dataset name: hex string}
                     Example: {'ischip': '56B4E9', 'chipdist': 'F0E442', 'isinsitu': '009E73', 'hasinsitu': 'E69F00'}
    """
    colors = [color_names[name] for (type, name, desc) in SUPP_ANNOTATIONS
              if name in highlights and gene_id in highlights[name]]
    print_highlights_table(colors, True)

def print_parameter_table(id, parameters, experiment_parameter_names, experiment_names):
    """Prints parameters table for the given gene id. If the number of
    parameters is high (greater than PARAMETER_INDEX_THRESHOLD), the table will
    have numbers inplace of parameter names and the table will be horizontal.
    Otherwise the table will be vertical.

    Parameters:
        id: gene id
        parameters: dictionary of experiment parameters:
                    {experiment id: {parameter name: value}}
                    Example: {1: {'rbf1_variance/disim1_rbf_variance': 0.59039292169555113,
                                  'disim1_variance': -5.9057868788275316,
                                  'disim1_decay': -3.9377851775471258,
                                  'disim1_di_variance': 0.0,
                                  'Basal1': -8.9106876980653453,
                                  'disim1_di_decay': -4.0190835928767878,
                                  'rbf1_inverseWidth/disim1_inverseWidth': -0.51096542027712455}
                             }

        experiment_parameter_names: dictionary mapping from experiment id
                                    to a list of parameter names:
                                    {experiment id: [parameter names]}
                                    Example: {1: ['rbf1_inverseWidth/disim1_inverseWidth',
                                                  'rbf1_variance/disim1_rbf_variance',
                                                  'disim1_di_decay',
                                                  'disim1_di_variance',
                                                  'disim1_decay',
                                                  'disim1_variance',
                                                  'Basal1']
                                             }

        experiment_names: dictionary mapping from experiment ids to names:
                          {experiment id: experiment name}
                          Example: {1: 'GPDISIM'}
    """
    all_parameter_names_temp = sum(experiment_parameter_names.values(), [])
    # remove duplicates
    all_parameter_names = []
    [all_parameter_names.append(name) for name in all_parameter_names_temp if not all_parameter_names.count(name)]

    # no parameters to show
    if all([len(d) == 0 for d in parameters.values()]):
        return

    if len(all_parameter_names) > PARAMETER_INDEX_THRESHOLD:
        print("""<table class="stats parameter_table">""")
        print("<tr>")
        print("""<th class="header">Parameters</th>""")
        for (col, name) in enumerate(all_parameter_names):
            print("""<th class="header">%s</th>""" % (col + 1))
        print("</tr>")

        for (exp_id, exp_name) in experiment_names.items():
            print("<tr>")
            print("""<td>%s</td>""" % exp_name)
            for name in all_parameter_names:
                if exp_id in parameters and name in parameters[exp_id]:
                    param = parameters[exp_id][name]
                    print("<td nowrap>%.2f</td>" % param)
                else:
                    print("<td></td>")
            print("</tr>")
        print("</table>")
    else:
        print("""<table class="stats parameter_table">""")
        print("<tr>")
        print("""<th class="header">Parameters</th>""")
        for (exp_id, exp_name) in experiment_names.items():
            print("""<th class="header">%s</th>""" % exp_name)
        print("</tr>")

        for name in all_parameter_names:
            print("<tr>")
            print("""<td>%s</td>""" % name)
            for (exp_id, exp_name) in experiment_names.items():
                if exp_id in parameters and name in parameters[exp_id]:
                    param = parameters[exp_id][name]
                    print("<td nowrap>%.2f</td>" % param)
                else:
                    print("<td></td>")
            print("</tr>")
        print("</table>")

def print_listing(browser_results, gene_ids, offset, highlights):
    """Prints the result listing.

    Parameters:
        browser_results: Results object

        gene_ids: list of ids of genes that will be in the listing
                  offset: list offset, i.e. the number of first gene in the
                  page highlights: dictionary mapping from supplementary
                  dataset name to list of gene ids having that highlight:
                  {supplementary dataset name: [gene ids]}
                  Example:
                    {'ischip': [4632, 8354, 10609], 'isinsitu': [], 'hasinsitu': [4632, 8354, 10609]}
        offset: result listing offset, i.e. the number of first gene result in page
    """
    dataset_figure = browser_results.get_dataset_figure()
    experiment_figures = browser_results.get_experiment_figures()

    experiment_parameters = browser_results.get_experiment_parameter_names()
    experiment_names = browser_results.get_experiment_names()

    print("""<table rules=rows frame=hsides>""")
    for id in gene_ids:
        offset += 1
        probe_name = browser_results.get_probe_name(id)
        aliases = browser_results.get_aliases(id)

        print("<tr>")
        print("<td>")
        print("<table>")
        print("<tr>")
        print("""<td class="alias">""")
        print("%d<br/>" % offset)
        print("Probe name: %s<br/>" % probe_name)

        # add a link to Entrez Gene database
        if 'ENTREZID' in aliases:
            url = "http://www.ncbi.nlm.nih.gov/gene/%s" % aliases['ENTREZID'][0]
            print("""<a href="%s">Gene in Entrez Gene database</a><br/>""" % url)

        print_alias_dict(aliases)
        print("</td>")
        print("</tr>")
        print("<tr>")
        print("""<td>""")
        print_highlights(id, highlights, SUPP_ANNOTATION_COLORS)
        print("</td>")
        print("</tr>")
        print("</table>")
        print("</td>")

        print_result(browser_results.get_experiment_results(id), browser_results.get_zscore(id), browser_results.get_supplementary_data(id), probe_name, dataset_figure, experiment_figures, id)
        print("<td>")
        print_parameter_table(id, browser_results.get_parameters(id), experiment_parameters, experiment_names)
        print("</td>")

        print("</tr>")
    print("</table>")

def get_supp_options(formdata):
    """Parses the supplementary options (highlight options) from
    the CGI query (i.e. formdata).

    Returns: list of supplementary options selected by the user:
             [(supplementary dataset name, symbol, value)]

    Example:
        [('hasinsitu', '=', '1.0'), ('ischip', '=', '0.0'), ('isinsitu', '=', '1.0')]
    """
    options = []
    for (type, name, desc) in SUPP_ANNOTATIONS:
        if name in formdata:
            if name + '_filtersymbol' in formdata: # integer or double condition
                symbol = parse_symbol(formdata.getvalue(name + '_filtersymbol'))
            else:
                symbol = '=' # boolean condition
            options.append((name, symbol, formdata.getvalue(name)))
    return options

def parse_symbol(symbol):
    """Parses symbol before it is used in an SQL query to prevent SQL
    injections.
    """
    return {'>':'>', '>=':'>=', '<':'<', '<=':'<=', '=':'='}[symbol]

def parse_search_entry(search):
    """Parses the search string into a list of gene names or aliases.
    Uses ',' (comma) as the delimiter.

    Returns: list of strings
    """
    return [s.strip(' \t\n\"\'') for s in search.strip().split(',')]

def ensure_database_not_writable(database_file):
    """Checks whether the given file exists and whether it is writable.
    If the file does not exist or if it is writable, an error message
    will be printed.
    """
    if not os.path.isfile(database_file):
        print_error_message("Database file '%s' not found" % os.path.join(os.getcwd(), database_file), True)
    if os.access(database_file, os.W_OK):
        print_error_message("Database file '%s' must not have write permissions" % os.path.join(os.getcwd(), database_file), True)

def generate_colors(annotations):
    """Returns a dictionary of annotation names and associated colors.

    Returns: {name, color hex string}
    """
    colors = {}
    for (type, name, desc) in annotations:
        colors[name] = COLOR_LIST[len(colors)]
    return colors

def print_highlight_statistics(highlights):
    """Prints highlight statistics. The number of different highlight
    combinations will be calculated and printed.

    Parameters:
        highlights: dictionary of supplementary dataset name and list of gene
                    ids to be highlighted:
                    {supplementary dataset name: [gene ids]}
                    Example:
                        {'ischip': [4632, 8354, 10609], 'isinsitu': [], 'hasinsitu': [4632, 8354, 10609]}
    """
    if len(SUPP_ANNOTATIONS) < 1 or len(highlights) == 0:
        return

    print("Highlights on this page:")
    names = list(highlights.keys())
    print("<table>")

    # Sort colors by supplementary data listing
    annotations = list(list(zip(*SUPP_ANNOTATIONS))[1])
    names.sort(key=lambda x: annotations.index(x))

    ids = set()
    for v in highlights.values():
        ids |= set(v)

    id_highlights = {}
    for id in ids:
        id_highlights[id] = []
        for name in names:
            if id in highlights[name]:
                id_highlights[id].append(name)

    counts = {}
    for comb in [tuple(x) for x in id_highlights.values()]:
        if comb in counts:
            counts[comb] += 1
        else:
            counts[comb] = 1

    keys = list(counts.keys())
    keys.sort(key=lambda x: annotations.index(x[0])) # Sort by supplementary data listing
    keys.sort(key=lambda x: len(x)) # Sort by color count
    for k in keys:
        v = counts[k]
        print("<tr><td>")
        colors = [SUPP_ANNOTATION_COLORS[name] for name in k]
        print_highlights_table(colors)
        print("</td><td>:%d<td>" % v)
        print("</tr>")
    print("</table>")

def print_parameter_index(browser_results):
    """Prints an index table of parameter names. This should be done when the
    number of parameters is high enough (PARAMETER_INDEX_THRESHOLD). The
    printed table consists of parameter names and associated indices.
    """
    names = browser_results.get_all_parameter_names()

    print("""<table class="stats parameter_table">""")
    print("<tr>")
    print("""<th class="header"></th>""")
    for (i, name) in enumerate(names):
        print("""<th class="header">%s</th>""" % (i + 1))
    print("</tr>")
    print("<tr>")
    print("<td>Parameter names</td>")
    for name in names:
        print("<td>%s</td>" % name)
    print("</tr>")
    print("</table>")

def print_error_message(message, print_header=False):
    """Prints an error message on the html page and terminates the execution of
    this script.

    Parameters:
        message: error message to print
        print_header: should this function also print the html headers
    """
    if print_header:
        print_headers("Result browser", MAX_FILTER_COUNT, "")
    print("<strong>Error: %s</strong>" % message)
    print_footer()
    sys.exit(1)

def show_figure(form):
    """'Prints' a PNG figure stored in the database.
    Uses 'figure_id' and 'gene_id' CGI parameters to select the figure from the
    database.
    """
    figure_id = form.getvalue('figure_id')
    gene_id = form.getvalue('gene_id')
    figuredata = db.get_figuredata(figure_id, gene_id)
    if not figuredata:
        sys.exit()
    print("Content-Type: image/png\nContent-Length: %d\n" % len(figuredata))

    # Python 3 compatibility: cannot use just print() as you have bypass the
    # unicode layer
    if sys.version_info[0] < 3:
        print(figuredata)
    else:
        sys.stdout.flush()
        sys.stdout.buffer.write(figuredata)
    sys.exit()

def show_about(form, db):
    """Prints the about page of tigreBrowser.
    """
    print_headers("About tigreBrowser", MAX_FILTER_COUNT, "")
    print("""<p>The <a href="http://users.ics.tkk.fi/ahonkela/tigre/">tigreBrowser software</a>
powering this site is Copyright (C) 2010 Miika-Petteri Matikainen,
Antti Honkela and Aalto University</p>""")
    l = []
    l.append(("tigreBrowser version", VERSION))
    l.append(("Database version", db.get_version()))
    l.append(("Number of genes in db", db.get_gene_count()))
    l.append(("Python version", platform.python_version()))

    print("""<table class="stats">""")
    for (k, v) in l:
        print("<tr>")
        print("<td>%s</td><td>%s</td>" % (k, v))
        print("</tr>")
    print("""<h2>Licensing information for tigreBrowser:</h2>
<p>
tigreBrowser is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see &lt;<a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>&gt;.""")
    print_footer()
    sys.exit()

def read_config_file(config_file):
    """Reads browser configuration from the config file.
    """
    global DATABASE_FILE, RANKING_TYPE
    config = RawConfigParser()
    if not config.read(config_file):
        if not config.read('../' + config_file):
            print_error_message("Config file '%s' not found" % config_file, True)
    try:
        DATABASE_FILE = config.get('tigreBrowser', 'database').strip('\'\"')
        type = config.get('tigreBrowser', 'ranking_type').strip('\'\"')
        if type.upper() == "TARGET":
            RANKING_TYPE = TARGET_RANKING
        elif type.upper() == "REGULATOR":
            RANKING_TYPE = REGULATOR_RANKING
        else:
            print_error_message("Config file: illegal ranking_type: '%s'<br/>Must be either 'target' or 'regulator'" % type, True)
    except (Exception,):
        e = sys.exc_info()[1] # Python >3.0 compatibility
        print_error_message(e, True)

def read_environment_config():
    """Reads environment variables RESULT_BROWSER_DATABASE to get the database
    filename and RESULT_BROWSER_RANKING_TYPE to get the ranking type.
    """
    global DATABASE_FILE, RANKING_TYPE
    if 'RESULT_BROWSER_DATABASE' in os.environ:
        DATABASE_FILE = os.environ['RESULT_BROWSER_DATABASE']
    if 'RESULT_BROWSER_RANKING_TYPE' in os.environ:
        type = os.environ['RESULT_BROWSER_RANKING_TYPE']
        if type.upper() == "TARGET":
            RANKING_TYPE = TARGET_RANKING
        elif type.upper() == "REGULATOR":
            RANKING_TYPE = REGULATOR_RANKING
        else:
            print_error_message("illegal ranking_type: '%s'<br/>Must be either 'target' or 'regulator'" % type, True)

def check_ranking_type(tfs, target_sets, ranking_type):
    """Checks whether the set ranking type is correct for the current database.
    Returns the correct ranking type.

    Parameters:
        tfs: list of TFs
        target_sets: list target sets
        ranking_type: ranking type to check
    """
    if not tfs and ranking_type == TARGET_RANKING and target_sets:
        return REGULATOR_RANKING
    if not target_sets and ranking_type == REGULATOR_RANKING and tfs:
        return TARGET_RANKING
    return ranking_type

def print_form_with_divs(form, results=None):
    """Prints search form and div-tags for the form.
    """
    print("""<div id="container">""")
    print_form(form, results)
    print("""<div id="results">""")
    print("""<a href="%s">About tigreBrowser</a><br/>""" % (SCRIPT_URI + "?show_about=1"))


t0 = time.clock()
form = cgi.FieldStorage()

VERSION = "1.0"
COLOR_LIST = ['E69F00', '56B4E9', '009E73', 'F0E442', '0072B2', 'D55E00', 'CC79A7', '000000']
MAX_FILTER_COUNT = 20
NUMBERS = ['5', '10', '20', '50', '100']
FILTER_SYMBOLS = ['&gt', '&gt=', '&lt', '&lt=', '=']
PARAMETER_INDEX_THRESHOLD = 10
SCRIPT_URI = os.getenv("SCRIPT_URI") or ""
REGULATOR_RANKING = 1
TARGET_RANKING = 2
CONFIG_FILE = "tigreBrowser.cfg"
DATABASE_FILE = None
RANKING_TYPE = None

read_config_file(CONFIG_FILE)
read_environment_config()
ensure_database_not_writable(DATABASE_FILE)

try:
    db = Database(DATABASE_FILE)
    TFs = db.get_regulators()
    TARGET_SETS = db.get_target_sets()
except (sqlite3.DatabaseError,):
    e = sys.exc_info()[1] # Python >3.0 compatibility
    print_error_message("database file: %s" % e, True)


# if 'show figure' is defined, load the figure from the db and print it instead
# of printing the result browser
if 'show_figure' in form and 'figure_id' in form and 'gene_id' in form:
    show_figure(form)

if 'show_about' in form:
    show_about(form, db)

SUPP_ANNOTATIONS = db.get_supplementary_annotations()
SUPP_ANNOTATION_COLORS = generate_colors(SUPP_ANNOTATIONS)
SORT_TYPES = db.get_experiment_names()
SORT_TYPES += [type + "_diff" for type in SORT_TYPES]
FILTER_TYPES = SORT_TYPES
FILTER_TYPES.append('zscore')
EXPERIMENT_SETS = db.get_experiment_sets()

script_url = os.getenv("SCRIPT_URL")
query_string = os.getenv("QUERY_STRING")
req = cgi.parse_qs(query_string)

RANKING_TYPE = check_ranking_type(TFs, TARGET_SETS, RANKING_TYPE)

if RANKING_TYPE == TARGET_RANKING:
    title = 'tigreBrowser: Target ranking'
elif RANKING_TYPE == REGULATOR_RANKING:
    title = 'tigreBrowser: Regulator ranking'
else:
    print_error_message("'ranking_type' must be either 'regulator' or 'target'", True)

filters_string, results_filters = get_filters_data(form)
print_headers(title, MAX_FILTER_COUNT, filters_string)

#print(form.keys())
#print(req)
#print("<br/>")
#print(script_url + urllib.urlencode(req, True))

#cgi.print_environ()
#cgi.print_directory()
#cgi.print_environ_usage()

if ('tf' in form or 'target_set' in form) and ('numgenes' in form and 'sort_type' in form or 'search_query' in form):
    exp_set = form.getvalue('experiment_set')
    tf = form.getvalue('tf')
    target_set = form.getvalue('target_set')
    experiment = form.getvalue('sort_type')
    supp_options = get_supp_options(form)

    num_genes = int(form.getvalue('numgenes'))
    offset = int(form.getvalue('offset'))

    search_genes = None
    if form.getvalue('search_query'):
        search_genes = parse_search_entry(form.getvalue('search_query'))

    if not form.getvalue('apply_filter'):
        results_filters = {}

    try:
        browser_results = results.Results(db, exp_set, tf, target_set, experiment, results_filters, supp_options, search_genes)
    except (Exception,):
        e = sys.exc_info()[1] # Python >3.0 compatibility
        print_form_with_divs(form)
        print("<hr>")
        print_error_message(e)

    gene_ids, count = browser_results.fetch_results(num_genes, offset)
    highlights = browser_results.get_highlights()

    print_form_with_divs(form, browser_results)
    print("<hr>")

    pages = int(math.ceil(float(count) / float(num_genes)))
    actpage = offset // int(num_genes)

    if search_genes:
        print('<strong>Search results for: "%s"</strong><br/>' % ', '.join(search_genes))
    print("Result count: %d<br/>" % count)
    print_highlight_statistics(highlights)

    if len(browser_results.get_all_parameter_names()) > PARAMETER_INDEX_THRESHOLD:
        print_parameter_index(browser_results)

    print_pages(pages, actpage, req, script_url, num_genes)
    print_listing(browser_results, gene_ids, offset, highlights)
    print_pages(pages, actpage, req, script_url, num_genes)

    print("""<div id=gene_namelist>""")
    print("<p>Gene name list:<br/>")
    print_genes([browser_results.get_probe_name(id) for id in gene_ids])
    print("</div>")
else:
    print_form_with_divs(form)

t1 = time.clock()

print("""<hr><p>The query took %f seconds.</p>""" % (t1-t0))
print("</div>")
print("</div>")

print_footer()
