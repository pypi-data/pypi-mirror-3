# -*- makefile -*-

top_srcdir = .
srcdir = .

SUBDIRS = doc

TXTS = 
HTML_TXTS = 
EXTRA_DIST =
CLEANFILES =

SCRIPTS += check-ws_sh2rst.sh

#TXTS += README.txt
#TXTS += README-inline-comments.txt
#TXTS += check-ws_sh2rst.txt
#CLEANFILES += check-ws_sh2rst.txt
#HTML_TXTS += README-GFDL.txt
#HTML_TXTS += README-COPYING.txt

TXT_HTMLS = $(patsubst %.txt,%.html,$(TXTS)) $(patsubst %.txt,%.html,$(HTML_TXTS))
TXT_PDFS = $(patsubst %.txt,%.pdf,$(TXTS))
TXT_TEXS = $(patsubst %.txt,%.tex,$(TXTS))
TXT_ODTS = $(patsubst %.txt,%.odt,$(TXTS))

CLEANFILES += $(TXT_HTMLS)
CLEANFILES += $(TXT_PDFS)
CLEANFILES += $(TXT_TEXS)
CLEANFILES += $(TXT_ODTS)

CLEANFILES += *.aux
CLEANFILES += *.log
CLEANFILES += *.out
CLEANFILES += *.toc
CLEANFILES += dist
CLEANFILES += MANIFEST

DISTFILES =
DISTFILES += Makefile
DISTFILES += $(TXTS)
DISTFILES += $(TXT_HTMLS)
DISTFILES += $(TXT_PDFS)
#DISTFILES += $(TXT_TEXS)
#DISTFILES += $(TXT_ODTS)
DISTFILES += $(JPGS)
DISTFILES += $(JPG_THUMBS)
DISTFILES += $(EXTRA_DIST)

%.html: %.txt
	cat $< | PYTHONPATH="$$( pwd )" tools/ws_rst2html.py --traceback --cloak-email-addresses >$@
	test -s $@ || (rm -f $@ && exit 1)

%.pdf: %.txt
	cat $< | PYTHONPATH="$$( pwd )" tools/ws_rst2pdf -e ws_docutils.raw_role >$@
	test -s $@ || (rm -f $@ && exit 1)

default: all

all: $(DISTFILES) all-local

all-local:

.PHONY: doc
doc:
	( cd doc && $(MAKE) )

clean: clean-local
	test -z '$(CLEANFILES)' || rm -rf $(CLEANFILES)

clean-local:
	( cd doc && $(MAKE) clean )

install_top_dir = $(top_srcdir)/../wolfmanx.bitbucket.org
install_dir = $(install_top_dir)/ws-docutils

install: all
	@(						\
	test ! -d $(install_top_dir) ||			\
	(						\
	mkdir -p $(install_dir);			\
	list='$(TXT_HTMLS)'; test -z "$$list" ||	\
	for file in $$list; do				\
	    dst_file="$$file";				\
	    test x"$file" = x"README.html" &&		\
	    dst_file="index.html";			\
	    echo "cp $$file $(install_dir)/$$dst_file";	\
	    cp $$file $(install_dir)/$$dst_file;	\
	done;						\
	list='$(JPGS)'; test -z "$$list" ||		\
	for file in $$list; do				\
	    echo "cp $$file $(install_dir)/";		\
	    cp $$file $(install_dir)/;			\
	done;						\
	list='$(JPG_THUMBS)'; test -z "$$list" ||	\
	for file in $$list; do				\
	    echo "cp $$file $(install_dir)/";		\
	    cp $$file $(install_dir)/;			\
	done;						\
	)						\
	)

dist:

tags-rc:
	gen_tags.sh --template
tags:
	gen_tags.sh --force

check-ws_sh2rst.txt: check-ws_sh2rst.sh
	./check-ws_sh2rst.sh >$@

# |:here:|
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' ()(eIDE-menu "z")

# :ide: COMPILE: tags
# . (let ((args "tags")) (compile (concat "make -k " args)))

# :ide: COMPILE: dist
# . (let ((args "dist")) (compile (concat "make -k " args)))

# :ide: COMPILE: install
# . (let ((args "install")) (compile (concat "make -k " args)))

# :ide: COMPILE: clean
# . (let ((args "clean")) (compile (concat "make -k " args)))

# :ide: COMPILE: doc
# . (let ((args "doc")) (compile (concat "make -k " args)))

# :ide: COMPILE: Standard
# . (let ((args "")) (compile (concat "make -k " args)))
#
# Local Variables:
# mode: makefile
# snip-mode: makefile-gmake
# truncate-lines: t
# End:
