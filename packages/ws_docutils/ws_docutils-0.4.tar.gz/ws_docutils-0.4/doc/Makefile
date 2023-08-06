# -*- makefile -*-

top_srcdir = ..
srcdir = .
tooldir = $(top_srcdir)/tools

TXTS = 
HTML_TXTS = 
JPGS = 
EXTRA_DIST =
CLEANFILES =

SCRIPTS += check-ws_sh2rst.sh

TXTS += README.txt
TXTS += README-inline-comments.txt
TXTS += check-ws_sh2rst.txt
CLEANFILES += check-ws_sh2rst.txt
HTML_TXTS += README-GFDL.txt
HTML_TXTS += README-BSD-sphinx.txt

CLEANFILES += *.aux
CLEANFILES += *.log
CLEANFILES += *.out
CLEANFILES += *.toc

# use cp for Windows
LN_S = cp
LN_S = ln -s

TXT_HTMLS = $(patsubst %.txt,%.html,$(TXTS)) $(patsubst %.txt,%.html,$(HTML_TXTS))
TXT_PDFS = $(patsubst %.txt,%.pdf,$(TXTS))
TXT_TEXS = $(patsubst %.txt,%.tex,$(TXTS))
TXT_ODTS = $(patsubst %.txt,%.odt,$(TXTS))

CLEANFILES += $(TXT_HTMLS)
CLEANFILES += $(TXT_PDFS)
CLEANFILES += $(TXT_TEXS)
CLEANFILES += $(TXT_ODTS)

JPG_THUMBS = $(patsubst %.jpg, %-t.jpg, $(JPGS))
#CLEANFILES += $(JPG_THUMBS)

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

%.html: %.txt docutils.conf
	cat $< | PYTHONPATH="$$( pwd ):$$( pwd )/.." $(tooldir)/ws_rst2html.py --traceback --cloak-email-addresses >$@
	test -s $@ || (rm -f $@ && exit 1)

%.pdf: %.txt docutils.conf
	cat $< | PYTHONPATH="$$( pwd ):$$( pwd )/.." $(tooldir)/ws_rst2pdf -e ws_docutils.raw_role >$@
	test -s $@ || (rm -f $@ && exit 1)

%-t.jpg: %.jpg
	convert $< -resize 200 $@

default: all

README.html: README.txt README-template.txt docutils.conf
	cat $< | PYTHONPATH="$$( pwd ):$$( pwd )/.." $(tooldir)/ws_rst2html.py --template README-template.txt --traceback --cloak-email-addresses >$@
	test -s $@ || (rm -f $@ && exit 1)

all: $(DISTFILES) all-local

all-local:

clean: clean-local
	test -z '$(CLEANFILES)' || rm -rf $(CLEANFILES)

clean-local:
	find . -name '*.pyc' | xargs -r rm 

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
	    test x"$$file" = x"README.html" &&		\
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

README.txt: ../README.txt
	rm -f $@
	$(LN_S) ../$@ $@

check-ws_sh2rst.txt: check-ws_sh2rst.sh
	./check-ws_sh2rst.sh >$@	
	test -s $@ || (rm -f $@ && exit 1)

z-massage-index.py: z-massage-index_.py ws_node.py
	adhoc.py $< >$@

# |:here:|
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' ()(eIDE-menu "z")

# :ide: COMPILE: z-massage-index.py
# . (let ((args "z-massage-index.py")) (compile (concat "make -k " args)))

# :ide: COMPILE: tags
# . (let ((args "tags")) (compile (concat "make -k " args)))

# :ide: COMPILE: dist
# . (let ((args "dist")) (compile (concat "make -k " args)))

# :ide: COMPILE: install
# . (let ((args "install")) (compile (concat "make -k " args)))

# :ide: COMPILE: clean
# . (let ((args "clean")) (compile (concat "make -k " args)))

# :ide: COMPILE: Standard
# . (let ((args "")) (compile (concat "make -k " args)))
#
# Local Variables:
# mode: makefile
# snip-mode: makefile-gmake
# truncate-lines: t
# End:
