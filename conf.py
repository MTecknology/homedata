#!/usr/bin/env python3
'''
Personal collection of random bits, with a sphinx-doc cover.

Build Dependencies: python3-sphinx python3-sphinx-rtd-theme
'''
import os


# Project Options
project = 'Home Data'
author = 'Michael Lustfield (MTecknology)'
copyright = '2026, Michael Lustfield'

# Oher documentation projects
exclude_patterns = [
        'README.rst',
        'projects/archive/gitlight/docs/*',
        ]

# HTML Output
html_theme = 'sphinx_rtd_theme'
html_show_sphinx = False
