.. -*- coding: utf-8 -*-
.. Copyright (C) 2011, Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
.. Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
.. .
.. This file is part of WSRFID.
.. .
.. Permission is granted to copy, distribute and/or modify this document
.. under the terms of the GNU Free Documentation License, Version 1.3
.. or any later version published by the Free Software Foundation;
.. with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
.. A copy of the license is included in the main documentation of WSRFID.
.. .
.. inline comments (with span/div extension)
.. .. role:: rem(span)
..    :format: ''
.. inline comments (with patched docutils)
.. role:: rem(raw)
   :format: never-ever
.. role:: html(raw)
   :format: html

####################################################
:rem:`|||:sec:|||`\ reStructuredText Inline Comments
####################################################
Where is the empty string?
##################################################

:Author: Wolfgang Scherer (at) gmx (dot) de

.. contents::

==================================================
:rem:`|||:sec:|||`\ Abstract
==================================================

This is an experimental document exploring the possibilities of
`reStructuredText`_ and `Docutils`_.
While setting up a templating environment to replace my old
README-to-XXX system, I ran into a couple of effects, which seemed
strange at first.

Although the document concentrates more on the lacking aspects of
`Docutils`_, I must emphasize that I am really impressed by its
features. Especially the excellent table support!

So here is the report of my adventurous journey into the belly of the
beast.

.. |one error| replace:: one (1) error
.. |two errors| replace:: two (2) errors
.. _one error:
.. _two errors:

.. Note:: Depending on the version of `Docutils`_, this document will
   generate either |one error| or |two errors| for undefined
   references. It will also produce a warning for the substitution
   definition of \||:error:||. And it may produce two(2) errors, when
   the substitutions \||:noexpansion:|| and \|||:error:||| are used.
   These errors and warnings are expected and cannot be avoided.

==================================================
:rem:`|||:sec:|||`\ Rationale for Inline Comments
==================================================

I really like tagging stuff. And therefore obviously meta-tagging as
well.

  #. It helps me navigate my documents and source code in a speedy
     manner (which is all the more necessary in Python).
  #. The document structure can be easily visualized with grep(1)
  #. Automatic processing of any kind!

However, tags should not be present in the final output and
comments are the preferred way to achieve that goal.

`reStructuredText`_ provides line comments, which can be used to tag
things::

  .. \|:tag:|
  Section Header
  --------------------------------------------------

But my standard tag extractor grep(1) does not show too much
information for a line like that:

>>> /bin/grep -nH -e  '|'':tag:|' README...
README...:26:  .. \|:tag:|

It is really desirable that the section title be displayed along with the
tag::

  |:tagi:| Section Header
  --------------------------------------------------

>>> /bin/grep -nH -e  '|'':tagi:|' README...
README...:39:  |:tagi:| Section Header

Other languages provide an inline or end-line comment syntax, which is
perfect for the purpose of tagging without adding the tag to the
output::

  #!/bin/sh
  echo 'Hello world!' # |:todo:| check, if there is a "world"
  echo 'How are you?'

>>> /bin/grep -nH -e  '|'':todo:|' README...
README...:49:  echo 'Hello world!' # |:todo:| check, if there is a "world"

But reStructuredText does not seem to provide an inline or end-line
comment.  And after going through the code, I can see why that is
so. (See also sections `Can of Worms`_ and `Proper Text Roles`_)

==================================================
:rem:`|||:sec:|||`\ Workarounds
==================================================

---------------------------------------------------------
\ :rem:`||:sec:||`\ Custom Role Based on **comment** Role
---------------------------------------------------------

This would do the trick [#]_::

     .. role:: rem(comment)

     :rem:`foo bar baz`

But **comment** is not a text role [#]_.

Well, it turns out, that I was overly naive to begin with ``:-)``.

------------------------------------------------------
\ :rem:`||:sec:||`\ Substitutions And The Empty String
------------------------------------------------------

Substitutions would be easy enough to provide for pseudo-comment-tags,
if only there was an empty string available::

  Title of the Day\ |:tit|

  .. This replacement does not actually work!
  .. |:tit:| replace:: `\ `

But there seems to be no such thing as an empty string in
reStructuredText.

One workaround is to use the unicode directive, which *only* adds a
blank::

  .. |:tit:| unicode:: U+0020

A better solution would be an option to the **replace** directive,
such as::

  .. This is not implemented!
  .. |:tit:| replace:: xxx
     :remove:

Such an option would also be generally useful.

But even if there was an empty string, it would still not allow level
tags such as::

  |||:tit:||| Section
  ||:tit:|| Subsection
  |:tit:| Sub-subsection

Although it is actually possible to define a substitution such as
\|||\:tit:|||, it is, however, not recognized when used::

   .. ||:noexpansion:|| replace:: is actually expanded
   .. The following definition is actually recognized and produces an error!
   .. <stdin>:259: (WARNING/2) Substitution definition "||:error:||" missing contents.
   .. |||:error:|||

   | This ||:noexpansion:|| is not expanded and produces and error with older `Docutils`_!
   | Newer `Docutils`_ do not raise an |||:error:||| here.

.. ||:noexpansion:|| replace:: is actually expanded
.. The following definition is actually recognized and produces an error!
.. <stdin>:259: (WARNING/2) Substitution definition "||:error:||" missing contents.
.. |||:error:|||

| This ||:noexpansion:|| is not expanded and produces and error with older `Docutils`_!
| Newer `Docutils`_ do not raise an ||:error:|| here.

And finally, title references do not include the substitution
expansion, but the substitution symbol text, this makes such
references pretty ugly and defeats the purpose of (meta-)tagging
altogether::

   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   |:tit:|\ Substitution Title Tag
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   See also `:tit:Substitution Title Tag`_

   .. |:tit:| unicode:: U+0020

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|:tit:|\ Substitution Title Tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See also `:tit:Substitution Title Tag`_

.. |:tit:| unicode:: U+0020

-------------------------------------------------------------------
\ :rem:`||:sec:||`\ Opening a Can of Worms -- The **raw** Directive
-------------------------------------------------------------------

`reStructuredText Interpreted Text Roles`_ offers a special **raw**
role to add stuff for a specific writer. It also warns:

.. warning:: "If you often need to use "raw"-derived interpreted text roles [...]
   that is a sign [...] that functionality may be missing from
   reStructuredText"

I heartily agree to that. And this is how an inline comment can be
implemented using this "stop-gap feature" [#]_::

  .. role:: rem(raw)
     :format: never-ever

This achieves the desired effect of an inline comment, which does not
leave a trace in the output::

  :rem:`|:tagses:|`\ paid

Here is an example:

  If you have not paid\ :rem:`your |:tagses:|`, you are in trouble.

.. _`Can of Worms`:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\   :rem:`|:sec:|`\ Eating a Couple (Parsing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Well, if it only was so easy ``;)``.

The `Docutils`_ package constructs the doctree fully agnostic of the
output format. Consequently, the significance of **raw** content
cannot be determined when parsing.

However, automatic title references are constructed when parsing and
therefore the entire raw text -- which in my case is ultimately to be
discarded -- is included in the text of title references (you may get
|two errors|_ for the references here):

  See `||\:sec:||Opening a Can of Worms -- the raw directive`_

This could be fixed with substitution references:

  See |Custom role based on raw directive|_

.. |Custom role based on raw directive| replace:: Custom role based on raw directive
.. _Custom role based on raw directive: `||\:sec:||Opening a Can of Worms -- the raw directive`_

But this is awkward and ugly.

In my humble opinion, that should actually be fixed [#astext]_.

With the patch `Gone Fishing #2`_ the following reference will work as
expected. Without the patch, |one error|_ is generated.

  See `Opening a Can of Worms -- the raw directive`_

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\   :rem:`|:sec:|`\ Spitting Them Out (Output)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While **HTML**, **LaTeX** and `rst2pdf`_ work fine, the **manpage**
writer effectively ignores the raw tag for all first level sections,
i.e., all raw text is included as if it was normal inline text
[#manpage]_::

  NAME
         |:sec:|reStructuredText Inline Comments - Where is the empty string?

  [..]

  |:SEC:|ABSTRACT

  [..]

  |:SEC:|CURRENT STATE

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\   :rem:`|:sec:|`\ Does Anybody Like These? (Other Applications)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is another caveat. `Trac`_ disables the **raw** role and gives
no option to enable it [#ftrac]_.

There is also no option for the **raw** role/directive in `Docutils`_
to silently ignore raw text. No, it must clutter the page with all
kinds of error messages [#duquiet]_::

  :rem:`|:sec:|`Abstract

  System Message: WARNING/2 (<string>, line 23); backlink
  raw (and derived) roles disabled

The funny thing is, that the raw text is actually still included in
the section title, which sort of defeats the purpose of disabling raw
``;)``.

.. _`Gone Fishing`:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\   :rem:`|:sec:|`\ Reading Instructions -- Gone Fishing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The correct solution seems to be, that **raw** nodes should not
deliver any text from their *astext*\() method, if the output
format is not known.

This could be achieved by:

#. an additional optional parameter to *nodes.raw.astext*\()::

     def astext(self, format = None):
         if format and format in self.get('format', '').split():
             return FixedTextElement.astext(self)
         return ''

   .. _`Gone Fishing #2`:

#. an additional static class attribute *output_format* in **nodes.raw**::

     output_format = None

     def astext(self):
         format = self.output_format
         if format and format in self.get('format', '').split():
             return FixedTextElement.astext(self)
         return ''

   Then the *output_format* attribute only needs to be set/reset once
   in the writer's *translate*\() method:

     | ``def translate(self):``
     |     **nodes.raw.output_format = 'manpage'**
     |     ``visitor = self.translator_class(self.document)``
     |     ``self.document.walkabout(visitor)``
     |     ``self.output = visitor.astext()``
     |     **nodes.raw.output_format = None**

Solution 2 is least invasive, since it only requires changes to the
**raw** node class definition and the *translate*\() method of all
writers. External code that inherits from `Docutils`_\ ' writers will not
break.

Only stand-alone external writers will break, if some document actually
uses the **raw** role/directive. However, the fix is really simple and
is also fully backward-compatible.

.. _`Proper Text Roles`:

==================================================
:rem:`|||:sec:|||`\ Proper Interpreted Text Roles
==================================================

The final solution I came up with is the span role/div directive which
heavily monkeypatches docutils.

It does provide the `remove` semantics required for inline comments
and fixes the `raw` role/directive as discussed.

.. ==================================================
..   \|||:sec:|||   Footnotes
.. ==================================================

:html:`<hr>`

.. [#] Or so I thought, before I saw the code ``;)``.

.. [#] It might as well be, since it would not be possible to create a
   **comment** text role that could behave any different than a real
   comment, unless the XML tag name is changed::

      <comment xml:space="preserve">
          -*- coding: utf-8 -*-

.. [#] `rst2pdf`_ misses an implementation for the **raw** role, but it
   can be easily added to genpdftext.py::

    class HandleRaw(NodeHandler, docutils.nodes.raw):
        def get_text(self, client, node, replaceEnt):
            text = ''
            if 'pdf' in node.get('format', '').split():
                text = node.astext()
                if replaceEnt:
                    text = escape(text)
        return text

.. [#astext] I know, that the output format is not known at parse
   time, and I have not checked the code.  But would it be hard to
   omit raw objects from the reference text [#manpage]_?
   ::

      <reference ids="id1" refid="sec-introduction">
          <raw classes="rem" format="never-ever" xml:space="preserve">
              |:tit:|
          Introduction

.. [#manpage] This is an actual bug in `Docutils`_. The manpage writer
   uses *node.astext*\() for first level sections instead of
   collecting the title by node tree traversal::

     self.body.append('.SH %s\n' % self.deunicode(node.astext().upper()))

   This is what includes the **raw** text anyway. However, it cannot
   be simply fixed by making *node.astext*\() skip raw nodes, because
   the manpage writer also does this::

     def visit_raw(self, node):
         if node.get('format') == 'manpage':
             self.body.append(node.astext() + "\n")

.. [#ftrac] This should really be the user's choice, so a `Trac`_ ini-option
   would be nice.

   I do not recommend enabling the **raw** role in `Trac`_, but
   here is how you do it::

        +++ trac/mimeview/rst.py
        -    'raw_enabled': 0})
        +    'raw_enabled': 1})

   If you just want raw text to disappear (as I do in this case), then
   you would be better off to patch `Docutils`_ and make the **raw**
   role fail silently by default [#duquiet]_.

.. [#duquiet] This should be fixed in `Docutils`_ with an option,
   e.g. **--no-raw-warnings**\ :rem:`|:diff:|`. Here is a patch how
   to implement it in ``/docutils/parsers/rst``::

     Index: __init__.py
     ===================================================================
     --- __init__.py    (revision 6508)
     +++ __init__.py    (working copy)
     @@ -131,6 +131,14 @@
                 'validator': frontend.validate_boolean}),
               ('Enable the "raw" directive.  Enabled by default.',
                ['--raw-enabled'],
     +          {'action': 'store_true'}),
     +         ('Suppress warnings when the "raw" directive is disable',
     +          ['--no-raw-warnings'],
     +          {'action': 'store_false', 'default': 1, 'dest': 'raw_warnings',
     +           'validator': frontend.validate_boolean}),
     +         ('Issue warnings when the "raw" directive is disabled.  '
     +          'Default is to issue warnings.',
     +          ['--raw-warnings'],
                {'action': 'store_true'}),))

          config_section = 'restructuredtext parser'
     Index: roles.py
     ===================================================================
     --- roles.py       (revision 6508)
     +++ roles.py       (working copy)
     @@ -295,9 +295,11 @@

      def raw_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
          if not inliner.document.settings.raw_enabled:
     -        msg = inliner.reporter.warning('raw (and derived) roles disabled')
     -        prb = inliner.problematic(rawtext, rawtext, msg)
     -        return [prb], [msg]
     +        if inliner.document.settings.raw_warnings:
     +            msg = inliner.reporter.warning('raw (and derived) roles disabled')
     +            prb = inliner.problematic(rawtext, rawtext, msg)
     +            return [prb], [msg]
     +        return [], []
          if 'format' not in options:
              msg = inliner.reporter.error(
                  'No format (Writer name) is associated with this role: "%s".\n'

.. ==================================================
..   \|||:sec:|||   References
.. ==================================================

.. |:fillme:| replace:: **missing fillme**
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _reStructuredText Interpreted Text Roles: http://docutils.sourceforge.net/docs/ref/rst/roles.html#raw
.. _Docutils: http://docutils.sourceforge.net
.. _rst2pdf: http://code.google.com/p/rst2pdf
.. _Perl: http://www.perl.org
.. _Python: http://www.python.org
.. _Jython: http://www.jython.org
.. _Java: http://www.java.com
.. _Qt: http://qt.nokia.com
.. _Mercurial: http://mercurial.selenic.com
.. _Trac: http://trac.edgewall.org
.. _Doxygen: http://www.doxygen.org
.. _Sphinx: http://sphinx.pocoo.org
.. _`GPL`: http://www.gnu.org/licenses/gpl.html
.. _doxypy: http://code.foosel.org/doxypy
.. _Abstract Syntax Trees: http://docs.python.org/library/ast.html
.. |Emacs| replace:: GNU Emacs
.. _Emacs: http://www.gnu.org/software/emacs

**Copyright**

Copyright (C) 2011, Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>.
Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de.
See the document source for conditions of use under the GNU Free
Documentation License.

.. ==================================================
..   \|||:sec:|||   END
.. ==================================================
.. 
.. :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
.. . M-x `eIDE-menu' ()(eIDE-menu "z")

.. :ide: CLN: Clean file (remove excess blank lines and whitespace)
.. . (let () (save-excursion (goto-char (point-min)) (set-buffer-modified-p t) (replace-regexp "\n\n\n+" "\n\n" nil) (c-beautify-buffer) (save-buffer)))

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
.. . (insert "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\:rem\:`|\:sec\:|`\\ |\:fillme\:|\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n" )

.. :ide: QUO: -- Subsection --
.. . (insert "--------------------------------------------------\n\:rem\:`||\:sec\:||`\\ |\:fillme\:|\n--------------------------------------------------\n" )

.. :ide: QUO: == Section ==
.. . (insert "==================================================\n\:rem\:`|||\:sec\:|||`\\ |\:fillme\:|\n==================================================\n" )

.. :ide: #-
.. . Sections ()

.. :ide: MENU-OUTLINE:  `|||:section:|||' (default)
.. . (x-eIDE-menu-outline "sec" '("|:" ":|") (cons (cons "^" ".. ") (cons nil nil)) "\\(_`[^`\n]+`\\|\\[[^]\n]+\\]\\|[|][^|\n]+[|]\\|[^:\n]+::\\)")

.. 
.. Local Variables:
.. mode: rst
.. snip-mode: rst
.. symbol-tag-symbol-regexp: "[-A-Za-z_]\\([-0-9A-Za-z_ ]*[-0-9A-Za-z_]\\|\\)"
.. symbol-tag-auto-comment-mode: nil
.. End:
