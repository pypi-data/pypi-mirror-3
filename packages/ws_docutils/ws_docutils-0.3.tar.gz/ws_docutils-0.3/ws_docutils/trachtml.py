# -*- coding: utf-8 -*-
# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This module has been placed in the public domain.
"""\
trachtml.py - docutils monkey patch to get icon for external links in trac.

usage: import ws_docutils.trachtml
"""

# --------------------------------------------------
# |||:sec:||| FUNCTIONS
# --------------------------------------------------

from docutils import nodes

def visit_reference(self, node):
    atts = {'class': 'reference'}
    if 'refuri' in node:
        atts['href'] = node['refuri']
        if ( self.settings.cloak_email_addresses
             and atts['href'].startswith('mailto:')):
            atts['href'] = self.cloak_mailto(atts['href'])
            self.in_mailto = 1
        atts['class'] += ' external'
        atts['class'] += ' ext-uri'
    else:
        assert 'refid' in node, \
               'References must have "refuri" or "refid" attribute.'
        atts['href'] = '#' + node['refid']
        atts['class'] += ' internal'
    if not isinstance(node.parent, nodes.TextElement):
        assert len(node) == 1 and isinstance(node[0], nodes.image)
        atts['class'] += ' image-reference'
    self.body.append(self.starttag(node, 'a', '', **atts))
    self.body.append('<span class="icon"> </span>')

import docutils.writers.html4css1
docutils.writers.html4css1.HTMLTranslator.visit_reference = visit_reference

# --------------------------------------------------
# |||:sec:||| MAIN
# --------------------------------------------------

# |:here:|
#
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' (eIDE-menu "z")

# :ide: SNIP: insert PROG-PATH
# . (snip-insert-mode "py_prog-path" nil t)

# :ide: CSCOPE ON
# . (cscope-minor-mode)

# :ide: CSCOPE OFF
# . (cscope-minor-mode (quote ( nil )))

# :ide: COMPILE: Run with --help
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --help")))

# :ide: COMPILE: Run with --test
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --test")))

# :ide: COMPILE: Run with --test --verbose
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --test --verbose")))

# :ide: INFO: Python Documentation
# . (let ((ref-buffer "*w3m*")) (if (get-buffer ref-buffer) (display-buffer ref-buffer t)) (other-window 1) (w3m-goto-url "http://docs.python.org/index.html" nil nil))

# :ide: INFO: Python Reference
# . (let ((ref-buffer "*python-ref*")) (if (not (get-buffer ref-buffer)) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " 'http://rgruet.free.fr/PQR26/PQR2.6.html'") ref-buffer) (display-buffer ref-buffer t)))

# :ide: COMPILE: Run w/o args
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " ")))
#
# Local Variables:
# mode: python
# comment-start: "#"
# comment-start-skip: "#+"
# comment-column: 0
# End:
