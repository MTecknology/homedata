#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Sphinxdoc Configuration for GitLight
'''
import os
import sys

sys.path.insert(0, os.path.abspath('../'))

def setup(app):
    os.system(os.path.realpath(__file__).replace('/conf.py', '/build-stubs'))


##
# General Configuration
##

## Version ##
version = u'0.0.1'
release = u'0.0.1'

## General ##
project = u'GitLight'
copyright = u'2018, GitLight Authors'
author = u'GitLight Authors'

modindex_common_prefix = ["gitlight."]

## Other ##
exclude_patterns = []
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'en'
today_fmp = '%d %b %Y'
extensions = [
    'sphinx.ext.autodoc',
    #'sphinx.ext.coverage',
    #'sphinx.ext.viewcode',
]
# add_module_names = True
pygments_style = 'sphinx'
todo_include_todos = True


##
# Output
##

## HTML ##
html_theme = 'alabaster'
#html_theme_path = []
html_title = u'GitLight'
html_logo = None
html_favicon = None
#html_static_path = ['_static']
html_last_updated_fmt = None
html_use_smartypants = False
#html_additional_pages = {}
html_show_sourcelink = False
html_show_sphinx = False
html_file_suffix = None
#htmlhelp_basename = 'GitLightdoc'  # Output file base name for HTML help builder.

## LaTeX ##
texinfo_documents = [
    (master_doc, 'GitLight', u'GitLight Documentation',
     author, 'GitLight', 'One line description of project.',
     'Miscellaneous'),
]
latex_documents = [
    (master_doc, 'GitLight.tex', u'GitLight Documentation',
     u'GitLight Authors', 'manual'),
]
# latex_logo = None

## Man Page ##
man_pages = [
    (master_doc, 'gitlight', u'GitLight Documentation',
     [author], 1)
]
