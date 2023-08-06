.. -*- coding: utf-8 -*-
.. Copyright (C) 2012, Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
.. Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
..
.. This file is part of Wiedenmann Docutils Extensions.
..
.. Permission is granted to copy, distribute and/or modify this document
.. under the terms of the GNU Free Documentation License, Version 1.3
.. or any later version published by the Free Software Foundation;
.. with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
.. A copy of the license is included in the main documentation of Wiedenmann Docutils Extensions.

.. inline comments (with span/div extension)
.. role:: rem(span)
   :format: ''
.. role:: html(span)
   :format: html
   :raw:

.. example roles for this document
.. role:: pdf(span)
   :format: pdf
.. role:: nhtml(span)
   :format: !html
.. role:: npdf(span)
   :format: !pdf

##################################################
:rem:`|||:sec:|||`\ WS Docutils Extensions
##################################################

:Author: `Wolfgang Scherer`_

.. contents::

==================================================
:rem:`|||:sec:|||`\ Purpose
==================================================

This package provides a `span` role and a `div` directive, fixes the
`raw` role for `Docutils`_ and provides a `raw_role` extension for
`rst2pdf`_.

The `span` role and the `div` directive are generalized from the `raw`
role and `raw`/\ `include` directives.

==================================================
:rem:`|||:sec:|||`\ In-Line Comments
==================================================

Among other things, the `span` role allows to define an interpreted
text role for a non-existing format which effectively provides inline
comments\ [#remove_is_sufficient]_.

E.g.::

    .. role:: rem(span)
       :format: ''

    ==================================================
    :rem:`|||:sec:|||`\ Purpose
    ==================================================

The `div` directive basically works the same way\ [#section_comment]_.

This ReST source, does not cause any output, if ws_docutils is active::

    .. div::
       :format: ''

       Elaborate Block comment ...

       ::

        ==================================================
        Quoted block trick to include Section Headers
        ==================================================

.. div::
   :format: ''

   Elaborate Block comment ...

   ::

    ==================================================
    Quoted block trick to include Section Headers
    ==================================================

.. [#remove_is_sufficient] Actually a *:remove:* role is sufficient
   for this task and may one day be part of `Docutils`_. But this
   project was really an experiment how far one could go with
   `Docutils`_. And I must say, I am really impressed.

.. [#section_comment] It is not possible to place section headers
   under a `div`. That would require extensive changes to the Docutils
   parser. And that is, when I gave up.

:rem:`produce a distance between footnote and next section header in output`

==============================================================================
:rem:`|||:sec:|||`\ Distance between Footnotes/Field Lists and Section Headers
==============================================================================

The HTML output (at least with my style sheets) lacks a distance, when
a section ends with a table element. Placing a span role comment on a
line by itself will generate an empty paragraph in the HTML output,
which solves the problem without changing the CSS.

Example::

    :field: list
    :item: 2

    :rem:`produce a distance between footnote and next section header in output`

:field: list
:item: 2

:rem:`produce a distance between field list and next section header in output`

=======================================================
:rem:`|||:sec:|||`\ Extended *:raw:*-like Functionality
=======================================================

The `span` role and the `div` directive work like an extended `raw`
role and `raw`/\ `include` directives.

--------------------------------------------------
:rem:`||:sec:||`\ `span` role: NOT FOR
--------------------------------------------------

It is possible to specify several formats instead of just one and it
is also possible to negate a format with e.g., ``!html`` to produce
output for all formats except HTML.

This input::

    This output is :nhtml:`not` HTML :npdf:`and`\ :pdf:`but` it is :npdf:`not` PDF.

Produces different output for HTML and PDF:

  This output is :nhtml:`not` HTML :npdf:`and`\ :pdf:`but` it is
  :npdf:`not` PDF.

---------------------------------------------------
:rem:`||:sec:||`\ `div` directive: Partial includes
---------------------------------------------------

Example `div` for HTML::

    .. div:: html
       :file: example.html
       :start-after: \|:here:| -->
       :end-before: <!-- \|:here:|
       :raw:

The specified part of `example.html`:

.. div::
   :file: example.html
   :start-after: \|:here:| -->
   :end-before: <!-- \|:here:|
   :literal:

is included as-is :pdf:`(but obviously not for PDF!)`:

.. div:: html
   :file: example.html
   :start-after: \|:here:| -->
   :end-before: <!-- \|:here:|
   :raw:

--------------------------------------------------
:rem:`||:sec:||`\ All `span` Role Options
--------------------------------------------------

I'm sorry not having enough time, so you have to consult the source
code in `role.py` to find out what they do.

::

    span_role.options = {
        'format': directives.unchanged,
        'literal': directives.flag,
        'raw': directives.flag,
        'pfx': directives.unchanged_required,
        'sfx': directives.unchanged_required,
        'ref': directives.flag,
        }

--------------------------------------------------
:rem:`||:sec:||`\ All `div` Directive Options
--------------------------------------------------

I'm sorry not having enough time, so you have to consult the source
code in `directive.py` to find out what they do.

::

    option_spec = {
        'format': directives.unchanged,
        'literal': directives.flag,
        'raw': directives.flag,
        'start-line': directives.nonnegative_int,
        'end-line': directives.nonnegative_int,
        'start-after': directives.unchanged_required,
        'end-before': directives.unchanged_required,
        'file': directives.path,
        'url': directives.uri,
        'tab-width': directives.nonnegative_int,
        'encoding': directives.encoding,
        'inline': directives.flag,
        'debug': directives.flag,
        }

==================================================
:rem:`|||:sec:|||`\ Shell Script Documenter
==================================================

The example python program `ws_sh2rst.py`, converts a shell script
into a ReST document.  (See `check-ws_sh2rst.sh - test for
ws_sh2rst.py`_).

It demonstrates, how tagging can be used to create automated
documentation. (It's sort of like a doxygen for sh(1) ``;-)``).

==================================================
:rem:`|||:sec:|||`\ Tool Scripts
==================================================

There are some scripts adapted from `Docutils`_ and `rst2pdf`_, which
include the span/div extension.

::

    tools/ws_rst2latex.py
    tools/ws_rst2man.py
    tools/ws_rst2man.py
    tools/ws_rst2odt.py
    tools/ws_rst2latex.py
    tools/ws_rst2pdf
    tools/ws_rst2html.py
    tools/ws_rst2pseudoxml.py
    tools/ws_sh2rst.py

==================================================
:rem:`|||:sec:|||`\ Installation/Source Code
==================================================

The package is available on `PyPI`_::

    $ easy_install ws_docutils

The source code is also available as a mercurial repository on
`bitbucket`_::

    $ hg clone https://bitbucket.org/wolfmanx/ws_docutils

==================================================
:rem:`|||:sec:|||`\ Historical Note
==================================================

This module was originally written for `Docutils`_ version 0.8 and
`rst2pdf`_ version 0.16.

Since it still works with `Docutils`_ version 0.8.1 and `rst2pdf`_
version 0.91, I decided I might as well publish it.

Since at the time I just started out to explore `Python`_, the code is
not very well written and I beg forgiveness for it not being actually
*pythonic*.

The orginal reasoning and baby steps that begat this gorilla patch are
available in `reStructuredText Inline Comments`_.

.. ==================================================
.. :rem:`|||:sec:|||`\ References
.. ==================================================

.. _`Python`: http://python.org
.. _`Docutils`: http://docutils.sourceforge.net/index.html
.. _`rst2pdf`: http://code.google.com/p/rst2pdf/

.. _`PyPI`: http://pypi.python.org/pypi/ws_docutils/
.. _`bitbucket`: https://bitbucket.org/wolfmanx/ws_docutils

.. _`reStructuredText Inline Comments`: README-inline-comments.html
.. _`check-ws_sh2rst.sh - test for ws_sh2rst.py`: check-ws_sh2rst.html

:rem:`|||:sec:|||`\ **Copyright**

Copyright (C) 2012, Wolfgang Scherer, <sw@wiedenmann-seile.de>.
Sponsored by `Wiedenmann-Seile GmbH`_.

The module source code is placed in the public domain following the
rest of `Docutils`_.

.. div::
   :format: html

   See section |GFDL| for license conditions of the documentation, and
   |BSD-sphinx| for some of the HTML stylesheets.

.. div::
   :format: !html

   See *GNU Free Documentation License* in file `GFDL.txt` for license
   conditions of the documentation, and *License for Sphinx* in file
   `LICENSE` for some of the HTML stylesheets.

.. |GFDL| replace:: `GNU Free Documentation License`_
.. |GPL| replace:: `GNU General Public License`_
.. |BSD-sphinx| replace:: `License for Sphinx`_

.. _`GNU Free Documentation License`: README-GFDL.html
.. _`GNU General Public License`: README-COPYING.html
.. _`License for Sphinx`: README-BSD-sphinx.html
.. _`Wiedenmann-Seile GmbH`: http://www.wiedenmannseile.de
.. _`Wolfgang Scherer`: sw@wiedenmann-seile.de

.. ==================================================
.. :rem:`|||:sec:|||`\ END
.. ==================================================
.. 
.. :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
.. . M-x `eIDE-menu' ()(eIDE-menu "z")

.. :ide: DELIM: SNIPPETS (ABOUT)       |q|<- SYM ->||,   ||<- SYM ->||,  @| SYM @
.. . (let nil (symbol-tag-normalize-delimiter (cons (cons nil "||<-") (cons "->||" nil)) t) (symbol-tag-switch-delimiter-sets) (symbol-tag-normalize-delimiter (cons (cons nil "||<-") (cons "->||" nil)) t) (setq symbol-tag-match-rx "sn[i]p") (setq symbol-tag-enclose-delimiter-set (symbol-tag-normalize-delimiter (cons (cons nil "@|") (cons "@" nil)))))

.. :ide: DELIM: SNIPPETS (DOC)          ||<- SYM ->||,     |: SYM :|,     ` SYM `
.. . (let nil (symbol-tag-normalize-delimiter (cons (cons nil "|:") (cons ":|" nil)) t) (symbol-tag-switch-delimiter-sets) (symbol-tag-normalize-delimiter (cons (cons nil "||<-") (cons "->||" nil)) t) (setq symbol-tag-match-rx "sn[i]p") (setq symbol-tag-enclose-delimiter-set (symbol-tag-normalize-delimiter (cons (cons "\\(\\`\\|[^\\]\\)" "`") (cons "`" nil)))))

.. :ide: DELIM: SNIPPETS (SNIP DOC)     ||<- SYM ->||,     |: SYM :|,     @ SYM @
.. . (let nil (symbol-tag-normalize-delimiter (cons (cons nil "|:") (cons ":|" nil)) t) (symbol-tag-switch-delimiter-sets) (symbol-tag-normalize-delimiter (cons (cons nil "||<-") (cons "->||" nil)) t) (setq symbol-tag-match-rx "sn[i]p") (setq symbol-tag-enclose-delimiter-set (symbol-tag-normalize-delimiter (cons (cons nil "@") (cons "@" nil)))))

.. :ide: DELIM: SNIPPETS (FILLME)       ||<- SYM ->||,     :: SYM ::,     @ SYM @
.. . (let nil (symbol-tag-normalize-delimiter (cons (cons nil "::") (cons "::" nil)) t) (symbol-tag-switch-delimiter-sets) (symbol-tag-normalize-delimiter (cons (cons nil "||<-") (cons "->||" nil)) t) (setq symbol-tag-match-rx "sn[i]p") (setq symbol-tag-enclose-delimiter-set (symbol-tag-normalize-delimiter (cons (cons nil "@") (cons "@" nil)))))

.. :ide: DELIM: SNIPPETS (SUBST)        ||<- SYM ->||,      @ SYM @,      @ SYM @
.. . (let nil (symbol-tag-normalize-delimiter (cons (cons nil "@") (cons "@" nil)) t) (symbol-tag-switch-delimiter-sets) (symbol-tag-normalize-delimiter (cons (cons nil "||<-") (cons "->||" nil)) t) (setq symbol-tag-match-rx "sn[i]p") (setq symbol-tag-enclose-delimiter-set (symbol-tag-normalize-delimiter (cons (cons "[^\\]" "`") (cons "`" nil)))))

.. :ide: +#-
.. . Snippet Delimiter Sets ()

.. :ide: DELIM: ReST (links)              ` SYM `_,    .. _` SYM `,      ` SYM `
.. . (let nil (symbol-tag-normalize-delimiter (cons (cons "[^\\]" "`") (cons "`_" nil)) t) (symbol-tag-switch-delimiter-sets) (symbol-tag-normalize-delimiter (cons (cons nil ".. _`") (cons "`:" nil)) t) (setq symbol-tag-enclose-delimiter-set (symbol-tag-normalize-delimiter (cons (cons "\\(\\`\\|[^\\]\\)" "`") (cons "`" nil)))))

.. :ide: DELIM: STANDARD (GNU quoting)    |: SYM :|,       :: SYM ::,     ` SYM '
.. . (let nil (symbol-tag-normalize-delimiter (cons (cons nil "::") (cons "::" nil)) t) (symbol-tag-switch-delimiter-sets) (symbol-tag-normalize-delimiter (cons (cons nil "|:") (cons ":|" nil)) t) (setq symbol-tag-enclose-delimiter-set (symbol-tag-normalize-delimiter (cons (cons nil "`") (cons "'" nil)))))

.. :ide: DELIM: STANDARD (ReST quoting)   |: SYM :|,       :: SYM ::,     ` SYM `
.. . (let nil (symbol-tag-normalize-delimiter (cons (cons nil "::") (cons "::" nil)) t) (symbol-tag-switch-delimiter-sets) (symbol-tag-normalize-delimiter (cons (cons nil "|:") (cons ":|" nil)) t) (setq symbol-tag-enclose-delimiter-set (symbol-tag-normalize-delimiter (cons (cons "[^\\]" "`") (cons "`" nil)))))

.. :ide: +#-
.. . Delimiter Sets ()

.. :ide: COMPILE: render reST as LaTeX
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | PYTHONPATH=\"$( pwd )\" tools/ws_rst2latex.py --traceback | tee " fn ".tex"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as MAN
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | PYTHONPATH=\"$( pwd )\" tools/ws_rst2man.py --traceback "))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as TXT (via MAN)
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | PYTHONPATH=\"$( pwd )\" tools/ws_rst2man.py --traceback | man -l -"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as ODT --strip-comments
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | PYTHONPATH=\"$( pwd )\" tools/ws_rst2odt.py --traceback --strip-comments | cat >" fn ".odt "))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as LaTeX, compile PDF and view with gv
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | PYTHONPATH=\"$( pwd )\" tools/ws_rst2latex.py --traceback | tee " fn ".tex && pdflatex '\\nonstopmode\\input " fn ".tex' && gv " fn ".pdf"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as PDF
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | PYTHONPATH=\"$( pwd )\" tools/ws_rst2pdf -e ws_docutils.raw_role >" fn ".pdf"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as HTML
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | PYTHONPATH=\"$( pwd )\" tools/ws_rst2html.py --traceback --cloak-email-addresses | tee " fn ".html "))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as pseudoXML
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " --traceback " fp " 2>&1 #| tee " fn ".pxml"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; PYTHONPATH=\"$( pwd )\" tools/ws_rst2pseudoxml.py " args))))

.. :ide: +#-
.. . Process ()

.. :ide: QUO: ~~ Subsubsection ~~
.. . (insert "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\:rem\:`|\:sec\:|`\\ ::fillme\::\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n" )

.. :ide: QUO: -- Subsection --
.. . (insert "--------------------------------------------------\n\:rem\:`||\:sec\:||`\\ ::fillme\::\n--------------------------------------------------\n" )

.. :ide: QUO: == Section ==
.. . (insert "==================================================\n\:rem\:`|||\:sec\:|||`\\ ::fillme\::\n==================================================\n" )

.. :ide: +#-
.. . Sections ()

.. :ide: MENU-OUTLINE:  `|||:section:|||' (default)
.. . (x-eIDE-menu-outline "sec" '("|:" ":|") (cons (cons "^" ".. ") (cons nil nil)) "\\(_`[^`\n]+`\\|\\[[^]\n]+\\]\\|[|][^|\n]+[|]\\|[^:\n]+::\\)")

.. 
.. Local Variables:
.. mode: rst
.. snip-mode: rst
.. truncate-lines: t
.. symbol-tag-symbol-regexp: "[-0-9A-Za-z_#]\\([-0-9A-Za-z_. ]*[-0-9A-Za-z_]\\|\\)"
.. symbol-tag-auto-comment-mode: nil
.. symbol-tag-srx-is-safe-with-nil-delimiters: nil
.. End:
