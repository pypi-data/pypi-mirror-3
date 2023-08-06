# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This module has been placed in the public domain.
"""
This module defines the div and span nodes.

It also adds default visit/depart handler to
docutils.nodes.NodeVisitor.
"""

__docformat__ = 'reStructuredText'

import sys
# (progn (forward-line 1) (snip-insert-mode "py.b.printf" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.sformat" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.printe" t) (insert "\n"))

# --------------------------------------------------
# |||:sec:||| NODES
# --------------------------------------------------

import docutils.nodes
from docutils.nodes import Special, PreBibliographic, Structural, Element, Inline, TextElement

class span(Inline, TextElement):
    # ||:cls:||
    """
    Data that is to be removed by the Parser or Writer for specific
    output formats.

    This is the inline version with text data.

    It also contains the static variables for both span and diversion
    nodes.
    """

    ext_initialized = False
    "Flag for remove directive/role, writer to perform setup."

    output_format = "*"
    """Output format that the text is to be removed for.
    If it is `*', the text is always removed.
    If it is None, the text is never removed (`keep` semantics).
    """

    @staticmethod
    def ext_init(settings):
        """Perform initialization."""
        if settings.span_enabled:
            # |:info:| do not change output format, so it can be overridden for 'rst2pdf'
            # docutils.nodes.span.output_format = '*'
            pass
        else:
            docutils.nodes.span.output_format = None
        import sys # |:debug:|
        span.ext_initialized = True;

    def astext(self):
        format_ = self.output_format
        # format = None => keep
        # format = '*' => Remove
        format_opt = self.get('format', '').split()
        if not (format_
                and (format_ == '*'
                     or format_ in self.get('format', '').split())):

            return TextElement.astext(self)
        return ''

class div(Special, PreBibliographic, Structural, Element):
    # ||:cls:||
    """
    Data that is to be removed by the Parser or Writer for specific
    output formats.

    This is the container version without data.

    The static variables for both span and diversion nodes are located
    in the span class.
    """

# install the `span` and `div` nodes.
docutils.nodes.span = span
docutils.nodes.div = div

# --------------------------------------------------
# |||:sec:||| FUNCTIONS
# --------------------------------------------------

import docutils.nodes

def visit_span(self, node): # ||:fnc:||
    """
    Called when entering a `span` node.

    Raise exception `SkipNode` if the nodes' format matches
    static class attribute `nodes.span.output_format`.
    """
    format_ = docutils.nodes.span.output_format
    import sys # |:debug:|
    nformat = node.get('format', '*')
    allowed = (format_
               and (format_ == '*'
                    or nformat == '*'
                    or format_ in nformat.split()))
    if node.get('drop',0):
        allowed = not allowed
    if allowed and True:                                   # |:debug:|
        return ''
    if format_ and format_ == 'pdf':
        # |:info:| rst2pdf does not use a proper writer, so cut off children right here
        node.children = []
    raise docutils.nodes.SkipNode

def depart_span(self, node): # ||:fnc:||
    """
    Called when leaving a `span` node.
    """
    pass

# install the NodeVisitor default handlers
docutils.nodes.NodeVisitor.visit_span = visit_span
docutils.nodes.NodeVisitor.depart_span = depart_span
docutils.nodes.NodeVisitor.visit_div = visit_span
docutils.nodes.NodeVisitor.depart_div = depart_span

# patch nodes.raw
def nodes_raw_astext(self):
    format_ = self.output_format
    if format_ and (format_ == '*'
                   or format_ in self.get('format', '').split()):
        return docutils.nodes.FixedTextElement.astext(self)
    return ''

docutils.nodes.raw.output_format = None
docutils.nodes.raw.astext = nodes_raw_astext

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
