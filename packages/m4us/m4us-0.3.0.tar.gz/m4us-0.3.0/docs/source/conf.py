# -*- coding: utf-8 -*-

# This file is part of Message For You Sir (m4us).
# Copyright © 2009-2012 Krys Lawrence
#
# Message For You Sir is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Message For You Sir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Message For You Sir.  If not, see <http://www.gnu.org/licenses/>.


# This file is execfile()d with the current directory set to its containing
# dir.
#
# Note that not all possible configuration values are present in this file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys, os

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
##sys.path.insert(0, os.path.abspath('.'))

# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
  'sphinx.ext.autodoc',
  'sphinx.ext.doctest',
  'sphinx.ext.intersphinx',
  'sphinx.ext.todo',
  'sphinx.ext.coverage',
  'sphinx.ext.viewcode',
  'sphinx.ext.graphviz',
  'sphinx.ext.inheritance_diagram',
  'repoze.sphinx.autointerface',
]

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
##exclude_patterns = []

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# A string with the fully-qualified name of a callable (or simply a class) that
# returns an instance of TemplateBridge. This instance is then used to render
# HTML documents, and possibly the output of other builders (currently the
# changes builder). (Note that the template bridge must be made theme-aware if
# HTML themes are to be used.)
##template_bridge = None

# A string of reStructuredText that will be included at the end of every source
# file that is read. This is the right place to add substitutions that should
# be available in every file.
##rst_epilog = ''

# A string of reStructuredText that will be included at the beginning of every
# source file that is read.
##rst_prolog = ''

# The name of the default domain. Can also be None to disable a default domain.
# The default is 'py'. Those objects in other domains (whether the domain name
# is given explicitly, or selected by a default-domain directive) will have the
# domain name explicitly prepended when named.
##primary_domain = 'py'

# The reST default role (used for this markup: `text`) to use for all
# documents.
default_role = 'term'

# If true, keep warnings as “system message” paragraphs in the built documents.
# Regardless of this setting, warnings are always written to the standard error
# stream when sphinx-build is run.
##keep_warnings = False

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '1.1'

# If true, Sphinx will warn about all references where the target cannot be
# found.
#nitpicky = False

# A list of (type, target) tuples that should be ignored when generating
# warnings in “nitpicky mode”. Note that type should include the domain name.
##nitpick_ignore = None


# -- Project information ------------------------------------------------------

# The documented project’s name.
project = u'Message For You Sir!'

# A copyright statement in the style '2008, Author Name'.
copyright = u'2009-2012, Krys Lawrence'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '0.3'
# The full version, including alpha/beta/rc tags.
release = '0.3.0'

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
##today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%Y-%m-%d'

# The default language to highlight source code in. The value should be a valid
# Pygments lexer name.
##highlight_language = 'python'

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = 'sphinx'

# If true, '()' will be appended to :func: etc. cross-reference text.
##add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
##show_authors = False

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['m4us.', 'm4us.core.']

# Trim spaces before footnote references that are necessary for the reST parser
# to recognize the footnote, but do not look too nice in the output.
trim_footnote_reference_space = True

# If true, doctest flags (comments looking like # doctest: FLAG, ...) at the
# ends of lines and <BLANKLINE> markers are removed for all code blocks showing
# interactive Python sessions (i.e. doctests). Default is true. See the
# extension doctest for more possibilities of including doctests.
trim_doctest_flags = True


# -- Options for internationalization -----------------------------------------

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


# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
##html_theme = 'default'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
##html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
##html_theme_path = []

# The style sheet to use for HTML pages. A file of that name must exist either
# in Sphinx’ static/ path, or in one of the custom paths given in
# html_static_path. Default is the stylesheet given by the selected theme. If
# you only want to add or override a few things compared to the theme’s
# stylesheet, use CSS @import to import the theme’s stylesheet.
##html_style = None

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
##html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
##html_short_title = None

# A dictionary of values to pass into the template engine’s context for all
# pages.
##html_context = {}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
##html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
##html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%Y-%m-%d'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = False

# Sphinx will add “permalinks” for each heading and description environment as
# paragraph signs that become visible when the mouse hovers over them.
#
# This value determines the text for the permalink. Set it to None or the empty
# string to disable permalinks.
##html_add_permalinks = "¶"

# Custom sidebar templates, maps document names to template names.
##html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
##html_additional_pages = {}

# If false, no module index is generated.
##html_domain_indices = True

# If false, no index is generated.
##html_use_index = True

# If true, the index is split into individual pages for each letter.
##html_split_index = False

# If true, the reST sources are included in the HTML build as _sources/name.
# Warning: If this config value is set to False, the JavaScript search function
# will only display the titles of matching documents, and no excerpt from the
# matching contents.
##html_copy_source = True

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
##html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
##html_file_suffix = '.html'

# Suffix for generated links to HTML files. The default is whatever
# html_file_suffix is set to; it can be set differently (e.g. to support
# different web server setups).
##html_link_suffix = None

# A string with the fully-qualified name of a HTML Translator class, that is, a
# subclass of Sphinx’ HTMLTranslator, that is used to translate document trees
# to HTML.
##html_translator_class = None

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
##html_show_copyright = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
##html_show_sphinx = True

# Encoding of HTML output files. Note that this encoding name must both be a
# valid Python encoding name and a valid HTML charset value.
##html_output_encoding = 'utf-8'

# If true, list items containing only a single paragraph will not be rendered
# with a <p> element. This is standard docutils behavior.
##html_compact_lists = True

# Suffix for section numbers. Set to " " to suppress the final dot on section
# numbers.
##html_secnumber_suffix = '. '

# Language to be used for generating the HTML full-text search index. This
# defaults to the global language selected with language. If there is no
# support for this language, "en" is used which selects the English language.
##html_search_language = None

# A dictionary with options for the search language support. The meaning of
# these options depends on the language selected.
##html_search_options = {}

# Output file base name for HTML help builder.
htmlhelp_basename = 'm4usdoc'


# -- Options for Epub output ---------------------------------------------------

# The basename for the epub file. It defaults to the project name.
##epub_basename = None

# The HTML theme for the epub output. Since the default themes are not
# optimized for small screen space, using the same theme for HTML and epub
# output is usually not wise. This defaults to 'epub', a theme designed to save
# visual space.
##epub_theme = 'epub'


# The title of the document. It defaults to the html_title option but can be
# set independently for epub creation.
##epub_title = None

# The author of the document. This is put in the Dublin Core metadata.
epub_author = u'Krys Lawrence'

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
##epub_identifier = ''

# The scheme of the identifier. Typical schemes are ISBN or URL.
##epub_scheme = ''

# A unique identification for the text.
##epub_uid = ''

# A tuple containing the cover image and cover page html template filenames.
##epub_cover = ()

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
##epub_pre_files = []

# HTML files shat should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
##epub_post_files = []

# A list of files that should not be packed into the epub file.
##epub_exclude_files = []

# The depth of the table of contents in toc.ncx.
##epub_tocdepth = 3

# Allow duplicate toc entries.
##epub_tocdup = True


# -- Options for LaTeX output -------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
  ('index', 'm4us.tex', u'Message For You Sir! Documentation',
   u'Krys Lawrence', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
##latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
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

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
##'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
##'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
##'preamble': '',
}

# A dictionary mapping 'howto' and 'manual' to names of real document classes
# that will be used as the base for the two Sphinx classes.
##latex_docclass = {'howto': 'article', 'manual': 'report'}

# A list of file names, relative to the configuration directory, to copy to the
# build directory when building LaTeX output. This is useful to copy files that
# Sphinx doesn’t copy automatically, e.g. if they are referenced in custom
# LaTeX added in latex_elements. Image files that are referenced in source
# files (e.g. via .. image::) are copied automatically.  You have to make sure
# yourself that the filenames don’t collide with those of any automatically
# copied files.
##latex_additional_files = []


# -- Options for text output --------------------------------------------------

# Determines which end-of-line character(s) are used in text output.
# (unix, windows, or native)
##text_newlines = 'unix'

# A string of 7 characters that should be used for underlining sections. The
# first character is used for first-level headings, the second for second-level
# headings and so on.
##text_sectionchars = '*=-~"+`'


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
  ('index', 'm4us', u'Message For You Sir! Documentation',
    [u'Krys Lawrence'], 1)
]

# If true, show URL addresses after external links.
##man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'm4us', u'Message For You Sir! Documentation',
    u'Krys Lawrence', 'Message For You Sir!',
    'One line description of project.', 'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
##texinfo_appendices = []

# If false, no module index is generated.
##texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
##texinfo_show_urls = 'footnote'

# A dictionary that contains Texinfo snippets that override those Sphinx
# usually puts into the generated .texi files.
##texinfo_elements = {}


# -- Options for the linkcheck builder ----------------------------------------

# A list of regular expressions that match URIs that should not be checked when
# doing a linkcheck build.
##linkcheck_ignore = []

# A timeout value, in seconds, for the linkcheck builder. Only works in Python
# 2.6 and higher. The default is to use Python’s global socket timeout.
##linkcheck_timeout = None

# The number of worker threads to use when checking links.
##linkcheck_workers = 5


# -- Options for extensions ---------------------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'python': ('http://docs.python.org', None)}

autodoc_member_order = 'groupwise'
autodoc_default_flags = ['members', 'show-inheritance']

todo_include_todos = True
