# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This module has been placed in the public domain.
"""
This module defines the interpreted text role functions for span
nodes.
"""

__docformat__ = 'reStructuredText'

# import sys
# (progn (forward-line 1) (snip-insert-mode "py.b.printf" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.sformat" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.printe" t) (insert "\n"))

from docutils import nodes, utils
from docutils.parsers.rst import directives
from docutils.parsers.rst.languages import en
from docutils.parsers.rst.roles import register_canonical_role, set_classes

import sys
def show_step(indx):
    return indx + 1

def span_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    import sys # |:debug:|

    def recursive_inliner_parse(text,lineno,inliner):
        # EXPERIMENTAL recursive parse
        import docutils.parsers.rst.states
        my_inliner = docutils.parsers.rst.states.Inliner()
        my_inliner.init_customizations(inliner.document.settings)
        my_memo = docutils.parsers.rst.states.Struct(
            document=inliner.document,
            reporter=inliner.document.reporter,
            language=inliner.language,
            title_styles=[],
            section_level=0,
            section_bubble_up_kludge=0,
            inliner=my_inliner)
        nodes_, msgs = my_inliner.parse(text, lineno, my_memo, inliner.parent)
        if len(msgs) > 0:
            msg = inliner.reporter.warning('span: internal parse error')
            prb = inliner.problematic(rawtext, rawtext, msg)
            return [prb], [msg].extend(msgs)
        return nodes_, []

    #indx=show_step(0)           # 0
    if not inliner.document.settings.span_enabled:
        msg = inliner.reporter.warning('span role disabled')
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    #indx=show_step(indx)        # 1
    if not nodes.span.ext_initialized:
        nodes.span.ext_init(inliner.document.settings)

    if 'format' in options:
        format_ = ' '.join(options['format'].lower().split())
        if (len(format_) >= 2
            and format_[0] == "'"
            and format_[-1] == "'"):
            format_ = format_[1:-1]
    else:
        format_ = '*'
    format_ = ' '.join(format_.lower().split())
    if format_.startswith('!'):
        drop = 1
        format_ = format_[1:].strip()
        if format_ == '':
            format_ = '*'
        elif format_ == '*':
            format_ = ''
    else:
        drop = 0
    options['format'] = format_
    options['drop'] = drop

    # not allowed for any output => remove
    if format_ == '':
        return [], []

    if 'literal' not in options:
        literal = 0
    else:
        literal = options['literal']
    options['literal'] = literal

    if 'raw' not in options:
        raw = 0
    else:
        raw = 1
    options['raw'] = raw

    if literal and raw:
        msg = inliner.reporter.error(
            '"Cannot both specify raw and'
            ' literal options.', line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    if 'pfx' in options:
        pfx = options['pfx']
        if (len(pfx) >= 2 and pfx[0] == "'" and pfx[-1] == "'"):
            pfx = pfx[1:-1]
    else:
        pfx = ''
    # del options['pfx'] # |:debug:|

    if 'sfx' in options:
        sfx = options['sfx']
        if (len(sfx) >= 2 and sfx[0] == "'" and sfx[-1] == "'"):
            sfx = sfx[1:-1]
    else:
        sfx = ''
    # del options['sfx'] # |:debug:|

    set_classes(options)

    if raw:
        text_nodes = [nodes.raw( rawtext, rawtext, **{})]
    else:
        if not inliner.document.settings.span_recursive:
            text = ''.join([ pfx, text, sfx ])
            text_nodes = [nodes.Text(utils.unescape(text), rawsource=utils.unescape(text, 1))]
        else:
            text_nodes = []
            if pfx:
                text_nodes.append( nodes.Text(utils.unescape(pfx), rawsource=utils.unescape(pfx, 1)))
            nodes_, msgs_ = recursive_inliner_parse(text,lineno,inliner)
            if len( msgs_ ):
                return nodes_, msgs_
            text_nodes.extend(nodes_)
            if sfx:
                text_nodes.append( nodes.Text(utils.unescape(sfx), rawsource=utils.unescape(sfx, 1)))
    
    node = nodes.span( '', '', *text_nodes, **options)
    return [node], []

span_role.options = {
    'format': directives.unchanged,
    'literal': directives.flag,
    'raw': directives.flag,
    'pfx': directives.unchanged_required,
    'sfx': directives.unchanged_required,
    'ref': directives.flag,
    }

# add role name to language en
en.roles['span']  = 'span'

# install `span` role
register_canonical_role('span', span_role)

# |:here:|
#
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' (eIDE-menu "z")

# :ide: CLN: Clean file (remove excess blank lines and whitespace)
# . (let () (save-excursion (goto-char (point-min)) (set-buffer-modified-p t) (replace-regexp "\n\n\n+" "\n\n" nil) (c-beautify-buffer) (save-buffer)))

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
