# -*- coding: utf-8 -*-
#
# C-PAC documentation build configuration file, created by
# sphinx-quickstart on Fri Jul 20 16:32:55 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import m2r
import os
import sys

from CPAC import __version__
from dateutil import parser as dparser
from github import Github
from github.GithubException import RateLimitExceededException, \
    UnknownObjectException

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('.'))

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.ifconfig',
              'sphinx.ext.intersphinx', 'sphinx.ext.viewcode',
              'sphinx.ext.mathjax', 'sphinxcontrib.programoutput', 'exec',
              'numpydoc']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.txt'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# A list of warning types to suppress arbitrary warning messages.
suppress_warnings = ['autosectionlabel.*']


# General information about the project.
project = 'C-PAC'
copyright = '2020, C-PAC Team'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = __version__


# Get tags from GitHub
# Set GITHUBTOKEN to your API token in your environment to increase rate limit.
g = Github(os.environ.get("GITHUBTOKEN"))

def _gh_rate_limit():
    print("""Release notes not updated due to GitHub API rate limit.

       MMM.           .MMM      __________________________________________
       MMMMMMMMMMMMMMMMMMM     |                                          |
       MMMMMMMMMMMMMMMMMMM     | Set GITHUBTOKEN to your API token in     |
      MMMMMMMMMMMMMMMMMMMMM    | your environment to increase rate limit. |
     MMMMMMMMMMMMMMMMMMMMMMM   | See CONTRIBUTING.md#environment-notes    |
    MMMMMMMMMMMMMMMMMMMMMMMM   |_   ______________________________________|
    MMMM::- -:::::::- -::MMMM    |/
     MM~:~ 00~:::::~ 00~:~MM
.. MMMMM::.00:::+:::.00::MMMMM ..
      .MM::::: ._. :::::MM.
         MMMM;:::::;MMMM
  -MM        MMMMMMM
  ^  M+     MMMMMMMMM
      MMMMMMM MM MM MM
           MM MM MM MM
           MM MM MM MM
        .~~MM~MM~MM~MM~~.
     ~~~~MM:~MM~~~MM~:MM~~~~
""")

try:
    gh_cpac = g.get_user("FCP-INDI").get_repo("C-PAC")
    gh_tags = [t.name for t in gh_cpac.get_tags()]
except RateLimitExceededException:
    _gh_rate_limit()
    gh_tags = []
gh_tags.sort(reverse=True)

# Try to get release notes from GitHub
try:
    gh_releases = []
    for t in gh_tags:
        try:
            gh_releases.append(gh_cpac.get_release(t).raw_data)
        except (AttributeError, UnknownObjectException):
            print(f"No notes for {t}")
    gh_releaseNotes = {r['tag_name']: {
        'name': r['name'],
        'body': r['body'],
        'published_at': r['published_at']
    } for r in gh_releases}
except RateLimitExceededException:
    _gh_rate_limit()
    gh_releaseNotes = {
        t: {
            "name": t,
            "body": f"See https://github.com/FCP-INDI/C-PAC/releases/tag/{t} for "
                    "release notes.",
            "published_at": None
        } for t in gh_tags
    }

def sort_tag(t):
    return(t[0:-4] if t[0].isdigit() else t[1:-4])

def _unireplace(release_note, unireplace):
    u = release_note.find('\\u')
    if (u!=-1):
        e = release_note[u:u+6]
        e2 = str(e[2:])
        release_note = release_note.replace(
            e,
            f" |u{e2}| "
        )
        unireplace[e2] = e
        return(_unireplace(release_note, unireplace))
    return(
        release_note,
            "\n\n".join([
            f".. |u{u}| unicode:: {v}"
        for u, v in list(unireplace.items())])
    )

this_dir = os.path.dirname(os.path.abspath(__file__))
release_notes_dir = os.path.join(this_dir, "release_notes")
if not os.path.exists(release_notes_dir):
    os.makedirs(release_notes_dir)
latest_path = os.path.join(release_notes_dir, 'latest.txt')
# all_release_notes = ""
for t in gh_tags:
    if t in gh_releaseNotes:
        tag_header = "{}{}{}".format(
            "Latest Release: " if t==gh_tags[0] else "",
            (
                gh_releaseNotes[t]['name'][4:] if (
                    gh_releaseNotes[t]['name'].startswith("CPAC")
                ) else gh_releaseNotes[t]['name'][5:] if (
                    gh_releaseNotes[t]['name'].startswith("C-PAC")
                ) else gh_releaseNotes[t]['name']
            ).strip(),
            " ({})".format(
                dparser.parse(gh_releaseNotes[t]['published_at']).date(
                ).strftime("%b %w, %Y")
            ) if gh_releaseNotes[t]['published_at'] else ""
        )
        release_note = "\n".join(_unireplace(
            """{}
{}
{}
""".format(
                tag_header,
                "^"*len(tag_header),
                m2r.convert(gh_releaseNotes[t]['body'].encode(
                    "ascii",
                    errors="backslashreplace"
                ).decode("utf-8"))
            ),
            {}
        ))

        release_notes_path = os.path.join(release_notes_dir, "{}.txt".format(t))
        if gh_releaseNotes[t]['published_at'] and not os.path.exists(
            release_notes_path
        ) and not os.path.exists(
            os.path.join(release_notes_dir, "v{}.txt".format(t))
        ):
            with open(release_notes_path, 'w+') as f:
                f.write(release_note)
        else:
            print(release_notes_path)

        if tag_header.startswith("Latest") and not os.path.exists(latest_path):
            with open(latest_path, 'w+') as f:
                f.write(
                    """

.. include:: /release_notes/{latest}.txt

.. toctree::
   :hidden:

   /release_notes/{latest}.txt
""".format(latest=str(t))
                )

rnd = [
    d for d in os.listdir(release_notes_dir) if d not in [
        "index.txt",
        "latest.txt"
    ]
]
rnd.sort(key=sort_tag, reverse=True)

all_release_notes = """
{}

.. toctree::
   :hidden:

   {}

""".format(
    "\n".join([
        ".. include:: /release_notes/{}".format(fp) for fp in rnd
    ]),
    "\n   ".join([
    "/release_notes/{}".format(d) for d in rnd
]))
with open(os.path.join(release_notes_dir, 'index.txt'), 'w+') as f:
    f.write(all_release_notes.strip())


# The full version, including alpha/beta/rc tags.
release = '{} Beta'.format(__version__)

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["futuredocs/*"]

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'classic'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "relbarbgcolor": "#0067a0",
    "sidebarbgcolor": "#f0f0f0",
    "sidebartextcolor": "#000000",
    "sidebarlinkcolor": "#0067a0",
    "headbgcolor": "#919d9d",
    "headtextcolor": "#e4e4e4"
}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ["../Themes"]

html_css_files = [
    'custom.css',
]

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/cpac_logo_vertical.png"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
  '**': [
    'globaltoc.html',
    'searchbox.html'
  ]
 }

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
html_file_suffix = ".html"

# Suffix for generated links to HTML files
html_link_suffix = ""
link_suffix = ""

# Output file base name for HTML help builder.
htmlhelp_basename = 'C-PACdoc'


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'C-PAC.tex', 'C-PAC Documentation',
   'C-PAC Team', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'c-pac', 'C-PAC Documentation',
     ['C-PAC Team'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'C-PAC', 'C-PAC Documentation',
   'C-PAC Team', 'C-PAC', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

rst_epilog = """

.. |Versions| replace:: {versions}

""".format(
    versions=", ".join(gh_tags[:5])
)
