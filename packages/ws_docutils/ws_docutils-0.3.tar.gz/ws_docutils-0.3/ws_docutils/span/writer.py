# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This module has been placed in the public domain.
"""
This module defines the writer support for span role and div
directive.
"""

# import sys
# (progn (forward-line 1) (snip-insert-mode "py.b.printf" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.sformat" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.printe" t) (insert "\n"))

import docutils.nodes
import docutils.writers
import docutils.writers.manpage
import docutils.writers.html4css1
import docutils.writers.latex2e
import docutils.writers.odf_odt

docutils.writers.manpage.Writer.output_format = 'manpage'
docutils.writers.html4css1.Writer.output_format = 'html'
docutils.writers.latex2e.Writer.output_format = 'latex'
docutils.writers.odf_odt.Writer.output_format = 'odt'

def write(self, document, destination):
    """
    Process a document into its final form.

    This is a wrapper around docutils.writers.Writer.write to
    implement the correct output_format setting for span/div/raw
    extensions. The original method is moved to
    docutils.writers.Writer.span_write.
    """
    import sys # |:debug:|
    try:
        raw_output_format = span_output_format = self.output_format
    except AttributeError:
        raw_output_format = '*'
        span_output_format = None
    try:
        raw_output_format_sv = docutils.nodes.raw.output_format
        have_raw_patch = True
    except AttributeError:
        have_raw_patch = False
    span_output_format_sv = docutils.nodes.span.output_format
    docutils.nodes.raw.output_format = raw_output_format
    # |:todo:| |:check:| sphinx does not have this setting. why?
    try:
        if document.settings.span_enabled:
            docutils.nodes.span.output_format = span_output_format
    except AttributeError:
        document.settings.span_enabled = True
        docutils.nodes.span.output_format = span_output_format
    output = self.span_write(document,destination)
    if have_raw_patch:
        docutils.nodes.raw.output_format = raw_output_format_sv
    docutils.nodes.span.output_format = span_output_format_sv
    return output

docutils.writers.Writer.span_write = docutils.writers.Writer.write
docutils.writers.Writer.write = write

# --------------------------------------------------
# |||:sec:||| END
# --------------------------------------------------
#
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' ()(eIDE-menu "z")

# :ide: CLN: Clean file (remove excess blank lines and whitespace)
# . (let () (save-excursion (goto-char (point-min)) (set-buffer-modified-p t) (replace-regexp "\n\n\n+" "\n\n" nil) (c-beautify-buffer) (save-buffer)))

# :ide: CSCOPE ON
# . (cscope-minor-mode)

# :ide: CSCOPE OFF
# . (cscope-minor-mode (quote ( nil )))

# :ide: COMPILE: Run w/o args
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " ")))
#
# Local Variables:
# mode: python
# comment-start: "#"
# comment-start-skip: "#+"
# comment-column: 0
# End:
