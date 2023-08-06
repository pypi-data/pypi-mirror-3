# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of everyapp.bootstrap.
# Copyright (C) 2010-2012 Krys Lawrence
#
# everyapp.bootstrap is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# everyapp.bootstrap is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

# everyapp.bootstrap documentation build configuration file, created by
# sphinx-quickstart on Tue Sep 21 00:09:10 2010, and then reformatted manually.
#
# This file is execfile()d with the current directory set to its containing
# directory.
#
# Note that not all possible configuration values are present in this
# auto-generated file.
#
# All configuration values have a default; values that are commented out serve
# to show the default.

"""Sphinx configuration for everyapp.bootstrap."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
import sys
import os

#---  Third-party imports
import pkg_resources

#---  Project imports


#---Globals--------------------------------------------------------------------

#---  Custom globals

# Note: This requires everyapp.bootstrap to be installed (e.g. with
# "python setup.py develop").
distribution = pkg_resources.get_distribution('everyapp.bootstrap')
_get_meta = lambda tag: [line for line in distribution.get_metadata_lines(
  'PKG-INFO') if line.startswith(tag + ':')][0][len(tag) + 2:]
author = _get_meta('Author')
home_page = _get_meta('Home-page')
title = distribution.project_name
file_name_base = '{distribution.key}-{distribution.version}'.format(
  distribution=distribution)
# This is needed because tags does not include the current builder until after
# the config file is loaded.
builder = (sys.argv[sys.argv.index('-b') + 1] if '-b' in sys.argv else 'html')


#---  General configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
  'sphinx.ext.autodoc',
##  'sphinx.ext.doctest',
  'sphinx.ext.intersphinx',
##  'sphinx.ext.graphviz',
##  'sphinx.ext.inheritance_diagram',
##  'sphinx.ext.coverage',
  'sphinx.ext.todo',
  'sphinx.ext.extlinks',
  'sphinx.ext.viewcode',
]

# The suffix of source file names.
##source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'contents'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
if builder != 'man':
    # We exclude the man directory for all non-"man" builders so that the man
    # files do not affect the index, etc.
    exclude_patterns = ['man/*']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# A string with the fully-qualified name of a callable (or simply a class) that
# returns an instance of TemplateBridge. This instance is then used to render
# HTML documents, and possibly the output of other builders.
##template_bridge = ''

# A string of reStructuredText that will be included at the end of every source
# file that is read. This is the right place to add substitutions that should
# be available in every file.
##rst_epilog = ''

# A string of reStructuredText that will be included at the beginning of every
# source file that is read.
##rst_prolog = ''

# The name of the default domain. Can also be None to disable a default domain.
##primary_domain = 'py'

# The reST default role (used for this markup: `text`) to use for all
# documents.
default_role = 'term'

# If true, keep warnings as “system message” paragraphs in the built documents.
##keep_warnings = False

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '1.1'

# If true, Sphinx will warn about all references where the target cannot be
# found.
nitpicky = True

# A list of (type, target) tuples that should be ignored when generating
# warnings in “nitpicky mode”. Note that type should include the domain name.
##nitpick_ignore = None


#---  Project information

# The documented project’s name.
project = distribution.project_name

# A copyright statement in the style '2008, Author Name'.
copyright = '2010-2012, ' + author

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = distribution.version
# The full version, including alpha/beta/rc tags.
release = distribution.version

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
##today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%Y-%m-%d'

# The default language to highlight source code in. The value should be a valid
# Pygments lexer name.
##highlight_language = 'python'

# The name of the Pygments (syntax highlighting) style to use.
##pygments_style = 'sphinx'

# If true, '()' will be appended to :func: etc. cross-reference text.
##add_function_parentheses = True

# If true, the current module name will be prepended to all description unit
# titles (such as .. function::).
##add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = True

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['everyapp.', 'everyapp.bootstrap.']

# Trim spaces before footnote references that are necessary for the reST parser
# to recognize the footnote, but do not look too nice in the output.
trim_footnote_reference_space = True

# If true, doctest flags (comments looking like # doctest: FLAG, ...) at the
# ends of lines are removed for all code blocks showing interactive Python
# sessions (i.e. doctests).
##trim_doctest_flags = True


#---  Options for internationalization

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
##language = None

# Directories in which to search for additional message catalogs, relative to
# the source directory. The directories on this path are searched by the
# standard gettext module.
#
# Internal messages are fetched from a text domain of sphinx; so if you add the
# directory ./locale to this settting, the message catalogs (compiled from .po
# format using msgfmt) must be in ./locale/language/LC_MESSAGES/sphinx.mo. The
# text domain of individual documents depends on gettext_compact.
##locale_dirs = []

# If true, a document’s text domain is its docname if it is a top-level project
# file and its very base directory otherwise.
#
# By default, the document markup/code.rst ends up in the markup text domain.
# With this option set to False, it is markup/code.
##gettext_compact = True


#---  Options for HTML output

# The theme to use for HTML and HTML Help pages.  See the documentation for a
# list of built-in themes.
##html_theme = 'default'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
##html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
##html_theme_path = []

# The style sheet to use for HTML pages. A file of that name must exist either
# in Sphinx’ static/ path, or in one of the custom paths given in
# html_static_path. Default is the style sheet given by the selected theme.
# If you only want to add or override a few things compared to the theme’s
# style sheet, use CSS @import to import the theme’s style sheet.
html_style = 'style.css'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = title

# A shorter title for the navigation bar.  Default is the same as html_title.
##html_short_title = None

# A dictionary of values to pass into the template engine’s context for all
# pages.
##html_context = {}

# The name of an image file (relative to this directory) to place at the top of
# the sidebar.
##html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
##html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the built-in static files,
# so a file named "default.css" will overwrite the built-in "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = today_fmt

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
##html_use_smartypants = True

# Sphinx will add “permalinks” for each heading and description environment as
# paragraph signs that become visible when the mouse hovers over them.
#
# This value determines the text for the permalink. Set it to None or the empty
# string to disable permalinks.
##html_add_permalinks = "¶"

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
  '**': [
    'globaltoc.html',
    'searchbox.html',
  ],
}

# Additional templates that should be rendered to pages, maps page names to
# template names.
##html_additional_pages = {}

# If false, no module index is generated.
##html_domain_indices = True

# If false, no index is generated.
##html_use_index = True

# If true, the index is split into individual pages for each letter.
##html_split_index = False

# If true, the reST sources are included in the HTML build.
# Warning: If this config value is set to False, the JavaScript search function
# will only display the titles of matching documents, and no excerpt from the
# matching contents.
##html_copy_source = True

# If true (and html_copy_source is true as well), links to the reST sources are
# added to the pages.
##html_show_sourcelink = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
html_use_opensearch = 'http://packages.python.org/everyapp.boostrap'

# This is the file name suffix for HTML files (e.g. ".xhtml").
##html_file_suffix = '.html'

# Suffix for generated links to HTML files. The default is whatever
# html_file_suffix is set to; it can be set differently (e.g. to support
# different web server setups).
##html_link_suffix = None

# A string with the fully-qualified name of a HTML Translator class, that is,
# a subclass of Sphinx’ HTMLTranslator, that is used to translate document
# trees to HTML. Default is None (use the built-in translator).
##html_translator_class = None

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
##html_show_copyright = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
##html_show_sphinx = True

# Encoding of HTML output files. Note that this encoding name must both be a
# valid Python encoding name and a valid HTML charset value.
##html_output_encoding = 'utf-8'

# If true, list items containing only a single paragraph will not be rendered
# with a <p> element. This is standard docutils behaviour.
##html_compact_lists = True

# Suffix for section numbers. Default: ". ". Set to " " to suppress the final
# dot on section numbers.
##html_secnumber_suffix = '. '

# Language to be used for generating the HTML full-text search index. This
# defaults to the global language selected with language. If there is no
# support for this language, "en" is used which selects the English language.
##html_search_language = None

# A dictionary with options for the search language support. The meaning of
# these options depends on the language selected.
##html_search_options = {}

# Output file base name for HTML help builder. It defaults to the project name.
##htmlhelp_basename = None


#---  Options for EPUB output

# The base name for the EPUB file. It defaults to the project name.
epub_basename = file_name_base

# The HTML theme for the EPUB output. Since the default themes are not
# optimized for small screen space, using the same theme for HTML and EPUB
# output is usually not wise. This defaults to 'epub', a theme designed to save
# visual space.
##epub_theme = 'epub'

# The title of the document. It defaults to the html_title option but can be
# set independently for epub creation.
##epub_title = None

# The author of the document. This is put in the Dublin Core metadata.
epub_author = author

# The language of the text. It defaults to the language option or en if the
# language is not set.
##epub_language = None

# The publisher of the document. This is put in the Dublin Core metadata. You
# may use any sensible string, e.g. the project homepage.
epub_publisher = epub_author

# The copyright of the document. It defaults to the copyright option but can be
# set independently for epub creation.
##epub_copyright = None

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
epub_identifier = home_page

# The scheme of the identifier. Typical schemes are ISBN or URL.
epub_scheme = 'URL'

# A unique identification for the text.
epub_uid = 'fde1cde8-36a7-4dc1-b0dd-d46ad809bbda'

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
##epub_pre_files = []

# HTML files shat should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
##epub_post_files = []

# A list of files that should not be packed into the EPUB file.
##epub_exclude_files = []

# The depth of the table of contents in toc.ncx.
epub_tocdepth = 2

# Allow duplicate toc entries.
epub_tocdup = False


#---  Options for LaTeX output

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual],
# toctree only).
latex_documents = [
  (master_doc, file_name_base + '.tex', title, author, 'manual', False),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
##latex_logo = None

# For "manual" documents, if this is true, then top level headings are parts,
# not chapters.
##latex_use_parts = False

# Documents to append as an appendix to all manuals.
##latex_appendices = []

# If false, no module index is generated.
##latex_domain_indices = True

# If true, show page references after internal links.
##latex_show_pagerefs = False

# If true, show URL addresses after external links.
##latex_show_urls = False

# A dictionary that contains LaTeX snippets that override those Sphinx usually
# puts into the generated .tex files.
# Keep in mind that backslashes must be doubled in Python string literals to
# avoid interpretation as escape sequences.
##latex_elements = {
##  # Paper size option of the document class ('a4paper' or 'letterpaper').
##  'papersize': 'letterpaper',
##  # Point size option of the document class ('10pt', '11pt' or '12pt').
##  'pointsize': '10pt',
##  # "babel" package inclusion.
##  'babel': '\\usepackage{babel}',
##  # Font package inclusion, default uses Times and Helvetica. You can set
##  # this to '' to use the Computer Modern fonts.
##  'fontpkg': '\\usepackage{times}',
##  # Inclusion of the "fncychap" package (which makes fancy chapter titles),
##  # default '\\usepackage[Bjarne]{fncychap}' for English documentation,
##  # '\\usepackage[Sonny]{fncychap}' for internationalized docs (because the
##  # "Bjarne" style uses numbers spelled out in English). Other "fncychap"
##  # styles you can try include "Lenny", "Glenn", "Conny" and "Rejne". You can
##  # also set this to '' to disable fncychap.
##  'fncychap': '\\usepackage[Bjarne]{fncychap}',
##  # Additional preamble content.
##  'preamble': '',
##  # Additional footer content (before the indices).
##  'footer': '',
##
##  # Keys that don’t need be overridden unless in special cases are:
##
##  # "inputenc" package inclusion.
##  'inputenc': '\\usepackage[utf8]{inputenc}',
##  # "fontenc" package inclusion.
##  'fontenc': '\\usepackage[T1]{fontenc}',
##  # "maketitle" call. Override if you want to generate a differently-styled
##  # title page.
##  'maketitle': '\\maketitle',
##  # "tableofcontents" call. Override if you want to generate a different
##  # table of contents or put content between the title page and the TOC.
##  'tableofcontents': '\\tableofcontents',
##  # "printindex" call, the last thing in the file. Override if you want to
##  # generate the index differently or append some content after the index.
##  'printindex': '\\printindex',
##  # Keys that are set by other options and therefore should not be overridden
##  # are: 'docclass', 'classoptions', 'title', 'date', 'release', 'author',
##  # 'logo', 'releasename', 'makeindex', 'shorthandoff'
##}

# A dictionary mapping 'howto' and 'manual' to names of real document classes
# that will be used as the base for the two Sphinx classes. Default is to use
# 'article' for 'howto' and 'report' for 'manual'.
##latex_docclass = None

# A list of file names, relative to the configuration directory, to copy to the
# build directory when building LaTeX output.  Image files that are referenced
# in source files are copied automatically. You have to make sure yourself that
# the file names don’t collide with those of any automatically copied files.
##latex_additional_files = []


#---  Options for text output

# Determines which end-of-line character(s) are used in text output.
# (unix, windows, or native)
##text_newlines = 'unix'

# A string of 7 characters that should be used for underlining sections. The
# first character is used for first-level headings, the second for second-level
# headings and so on.
##text_sectionchars = '*=-~"+`'


#---  Options for manual page output

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
  ('man/mkbootstrap', 'mkbootstrap', u'Create virtualenv bootstrap scripts',
    [author], 1),
  ('man/bootstrap.py', 'bootstrap.py', u'Bootstrap the development environemnt'
    ' for a project', [author], 1),
  ('man/bootstrap.cfg', 'bootstrap.cfg', u'Configuration file for '
    'bootstrap.py', [author], 5),
]

# If true, show URL addresses after external links.
##man_show_urls = False


#---  Options for Texinfo output

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
##texinfo_documents = [
##  (master_doc, file_name_base, title, author, title,
##    'One line description of project.', 'Miscellaneous'),
##]

# Documents to append as an appendix to all manuals.
##texinfo_appendices = []

# If false, no module index is generated.
##texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
##texinfo_show_urls = 'footnote'

# A dictionary that contains Texinfo snippets that override those Sphinx
# usually puts into the generated .texi files.
##texinfo_elements = {}


#---  Options for the linkcheck builder

# A list of regular expressions that match URIs that should not be checked when
# doing a linkcheck build.
##linkcheck_ignore = []

# A timeout value, in seconds, for the linkcheck builder. Only works in Python
# 2.6 and higher. The default is to use Python’s global socket timeout.
##linkcheck_timeout = None

# The number of worker threads to use when checking links.
##linkcheck_workers = 5


#---  Options for extension modules

# This value selects what content will be inserted into the main body of an
# autoclass directive. The possible values are: 'class', 'both', 'init'.
##autoclass_content = 'class'

# This value selects if automatically documented members are sorted
# alphabetically (value 'alphabetical'), by member type (value 'groupwise') or
# by source order (value 'bysource').
autodoc_member_order = 'bysource'

# This value is a list of autodoc directive flags that should be automatically
# applied to all autodoc directives. The supported flags are 'members',
# 'undoc-members', 'inherited-members' and 'show-inheritance'.
autodoc_default_flags = ['members', 'show-inheritance']

# A list of directories that will be added to sys.path when the doctest builder
# is used. (Make sure it contains absolute paths.)
##doctest_path  = []

# Python code that is treated like it were put in a testsetup directive for
# every file that is tested, and for every group. You can use this to e.g.
# import modules you will always need in your doctests.
##doctest_global_setup = ''

# If this is a nonempty string, standard reST doctest blocks will be tested
# too. They will be assigned to the group name given.
##doctest_test_doctest_blocks = 'default'

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'python': ('http://docs.python.org/', None)}

# The maximum number of days to cache remote inventories, in days. Set this to
# a negative value to cache inventories for unlimited time.
##intersphinx_cache_limit = 5

# The command name with which to invoke dot. You may need to set this to a full
# path if dot is not in the executable search path.
##graphviz_dot = 'dot'

# Additional command-line arguments to give to dot, as a list. This is the
# right place to set global graph, node or edge attributes via dot’s -G, -N and
# -E options.
##graphviz_dot_args = []

# The output format for graphviz when building HTML files. This must be either
# 'png' or 'svg'.
##graphviz_output_format = 'png'

# A dictionary of graphviz graph attributes for inheritance diagrams.
# For example: inheritance_graph_attrs = dict(rankdir="LR", size='"6.0, 8.0"',
# fontsize=14, ratio='compress')
##inheritance_graph_attrs = {}

# A dictionary of graphviz node attributes for inheritance diagrams.
# For example: inheritance_node_attrs = dict(shape='ellipse', fontsize=14,
# height=0.75, color='dodgerblue1', style='filled')
##inheritance_node_attrs = {}

# A dictionary of graphviz edge attributes for inheritance diagrams.
##inheritance_edge_attrs = {}

# If this is True, todo and todolist produce output, else they produce nothing.
todo_include_todos = True

# Coverage configuration options.
##coverage_ignore_modules = None
##coverage_ignore_functions = None
##coverage_ignore_classes = None
##coverage_c_path = None
##coverage_c_regexes = None
##coverage_ignore_c_items = None

# This config value must be a dictionary of external sites, mapping unique
# short alias names to a base URL and a prefix. For example, to create an alias
# for the above mentioned issues, you would add
# extlinks = {'issue': ('http://bitbucket.org/birkenfeld/sphinx/issue/%s',
# 'issue ')}
extlinks = {
  'issue': ('http://bitbucket.org/everyapp/bootstrap/issue/%s', 'issue '),
}


#---Functions------------------------------------------------------------------

def setup(app):
    # We use ≥ in INSTALL.txt.  This adds support for it to latex.
    from sphinx.util.texescape import tex_replacements
    tex_replacements.append((u'≥', ur'$\geq$'))
    # The man builder needs a different doctree cache directory because we
    # alter the exclude_patterns option above.
    if builder == 'man':
        app.doctreedir = os.path.join(app.doctreedir, 'man')


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
##sys.path.insert(0, os.path.abspath('.'))


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
