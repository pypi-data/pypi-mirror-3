#!/usr/bin/python

# Author: 
# Contact: grubert@users.sf.net
# Copyright: This module has been placed in the public domain.
# Modified to import ws_docutils.span by <Wolfgang.Scherer@gmx.de>

"""
man.py
======

This module provides a simple command line interface that uses the
man page writer to output from ReStructuredText source.
"""

import locale
try:
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description
from docutils.writers import manpage
import ws_docutils.span

description = ("Generates plain unix manual documents.  " + default_description)

publish_cmdline(writer=manpage.Writer(), description=description)
