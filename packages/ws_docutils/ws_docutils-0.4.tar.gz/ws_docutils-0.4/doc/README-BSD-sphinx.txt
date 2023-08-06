.. -*- coding: utf-8 -*-
.. \||<-snip->|| start
.. Copyright (C) 2012, Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
.. Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
..
.. This file is part of Wiedenmann Vacation.
..
.. Permission is granted to copy, distribute and/or modify this document
.. under the terms of the GNU Free Documentation License, Version 1.3
.. or any later version published by the Free Software Foundation;
.. with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
.. A copy of the license is included in the main documentation of Wiedenmann Vacation.

.. inline comments (with ws_docutils)
.. role:: rem(span)
   :format: ''
.. role:: html(span)
   :format: html
   :raw:

.. \||<-snap->|| include ^index-header.snip$

.. Include the sphinx BSD license verbatim
.. include:: LICENSE
   :literal:

.. \||<-snap->|| include ^index-footer.snip$
.. \||<-snip->|| stop

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
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | ws_rst2latex.py --traceback | tee " fn ".tex"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as MAN
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | ws_rst2man.py --traceback "))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as TXT (via MAN)
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | ws_rst2man.py --traceback | man -l -"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as ODT --strip-comments
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | ws_rst2odt.py --traceback --strip-comments | cat >" fn ".odt "))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as LaTeX, compile PDF and view with gv
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | ws_rst2latex.py --traceback | tee " fn ".tex && pdflatex '\\nonstopmode\\input " fn ".tex' && gv " fn ".pdf"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as PDF
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | ws_rst2pdf -e ws_docutils.raw_role >" fn ".pdf"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as HTML
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | ws_rst2html.py --traceback --cloak-email-addresses | tee " fn ".html "))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. :ide: COMPILE: render reST as pseudoXML
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " --traceback " fp " 2>&1 #| tee " fn ".pxml"))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; ws_rst2pseudoxml.py " args))))

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
