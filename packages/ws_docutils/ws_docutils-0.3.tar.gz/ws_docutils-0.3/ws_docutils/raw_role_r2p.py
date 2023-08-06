# -*- coding: utf-8 -*-
# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This module has been placed in the public domain.

import os
from xml.sax.saxutils import escape
from rst2pdf.log import log, nodeid
from rst2pdf.basenodehandler import NodeHandler
import docutils.nodes
from urlparse import urljoin, urlparse
from reportlab.lib.units import cm
from rst2pdf.opt_imports import Paragraph

from rst2pdf.image import MyImage, missing
import ws_docutils.span

class HandleRaw(NodeHandler, docutils.nodes.raw):
    def get_text(self, client, node, replaceEnt):
        text = ''
        if 'pdf' in node.get('format', '').split():
            docutils.nodes.raw.output_format = 'pdf'
            text = node.astext()
            if replaceEnt:
                text = escape(text)
        return text
