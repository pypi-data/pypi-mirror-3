# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This module has been placed in the public domain.
"""
This module defines the span role and div directive.

It sets up command line options and splices the various definitions
into the docutils modules.
"""

# --------------------------------------------------
# |||:sec:||| CONFIGURATION
# --------------------------------------------------

from docutils import frontend
import docutils.parsers.rst

span_settings = [
    ('Disable the "span" role and "div" directive; " '
     'replaced with a "warning system message.',
     ['--no-span'],
     {'action': 'store_false', 'default': 1, 'dest': 'span_enabled',
      'validator': frontend.validate_boolean}),
    ('Enable the "span" role and "div" directive.  Enabled by default.',
     ['--span-enabled'],
     {'action': 'store_true'}),
    ('Disable "span" role recursive parsing. '
     'Disbled by default.',
     ['--no-span-recursive'],
     {'action': 'store_false', 'default': 0, 'dest': 'span_recursive',
      'validator': frontend.validate_boolean}),
    ('Enable "span" role recursive parsing.',
     ['--span-recursive'],
     {'action': 'store_true'}),
    ]

ss = list(docutils.parsers.rst.Parser.settings_spec)
opts = list(ss[2])
opts.extend(span_settings)
ss[2] = tuple(opts)
docutils.parsers.rst.Parser.settings_spec = tuple(ss)

# --------------------------------------------------
# |||:sec:||| SETUP
# --------------------------------------------------

# install `span` and `div` nodes
import ws_docutils.span.nodes
# install `span` role
import ws_docutils.span.role
# install `div` directive
import ws_docutils.span.directive
# install writer support
import ws_docutils.span.writer

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
