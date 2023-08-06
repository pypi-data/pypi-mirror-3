#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This module has been placed in the public domain.
"""\
sh2rst.py - sh(1) scripts to reStructuredText

usage: sh2rst.py [OPTIONS] []

OPTIONS
  -t, --test     run doctests
  -v, --verbose  verbose test output
  -h, --help     display this help message
"""

# --------------------------------------------------
# |||:sec:||| CONFIGURATION
# --------------------------------------------------

import sys
import os
import re

##
# reStructuredText header.
rst_header = """\
.. -*- rst -*-
.. role:: rem(span)
   :format: ''
"""

rst_contents = """
.. contents::
"""

rst_contents_before_header = False

# --------------------------------------------------
# |||:sec:||| CLASSES
# --------------------------------------------------

# --------------------------------------------------
# |||:sec:||| FUNCTIONS
# --------------------------------------------------

def rem( str_, lead_ws = False ): # ||:fnc:||
    if lead_ws:
        return ''.join(("\\ :rem:`", str_, "`"))
    return ''.join((":rem:`", str_, "`\\ "))

def sec(str_ = "|||" ":sec:|||", plain = False): # ||:fnc:||
    if plain:
        return str_
    return rem(str_)

# state variables
_in_body = False
_pend_nl = False

def header(title):               # ||:fnc:||
    global rst_header
    global rst_contents
    sline = "{0} {1}".format(sec(), title)
    ouline = "#" * len(sline)
    ousec = "-" * 50
    if rst_contents_before_header:
        first = ''.join((rst_header, rst_contents))
        second = ""
    else:
        first = rst_header
        second = rst_contents
        
    hd = "\n".join((
            first,
            ouline, sline, ouline,
            second,
            ousec, 'SYNOPSIS', ousec,
            ))
    rst_header = ""
    rst_contents = ""
    return hd

def outline(line=''):            # ||:fnc:||
    global _in_body
    global _pend_nl
    if not line:
        if _in_body:
            _pend_nl = True
        return
    elif not _in_body:
        print(header(line))
        _in_body = True
        _pend_nl = True
        return
    if _pend_nl:
        print('')
        _pend_nl = False
    print line

def run():                      # ||:fnc:||
    global _in_body
    global _pend_nl
    files = sys.argv[1:]
    if len(files) > 1:
        global rst_contents_before_header
        rst_contents_before_header = True
    if not files:
        files = ('-')
    # handle all files
    for file_ in files:
        if file_ == '-':
            fn = '<stdin>'
            fh = sys.stdin
            do_close = False
        else:
            fn = os.path.basename( file_ )
            fh = open(file_, "rb")
            do_close = True
        contents = fh.read()
        if do_close:
            fh.close()
        lines = re.split('[ \t\r]*\n', contents)
        _in_body = False
        in_descr = True
        lineno = 0
        # handle all lines
        for line in lines:
            lineno += 1
            # stop on \f
            if line.find('\f') >= 0:
                break
            line = line.rstrip()
            if not line:
                outline()
                continue
            mo = re.match('^# ?(.*)', line)

            # comment line
            if mo:
                if not in_descr:
                    outline()
                    in_descr = True
                line = mo.groups()[ 0 ]
                if not line:
                    outline()
                    continue
                # she-bang
                if line.startswith( '!/' ):
                    continue
                # emacs definition/python coding
                if line.startswith( '-*-' ):
                    continue
                # double comment
                if line.startswith( '#' ):
                    continue
                # handle tags
                first = True
                pre = []
                while True:
                    #                 1      2    3      4    5
                    mo = re.match('''^([^|]*)(\|+)(:[^:]+:)(\|+)(.*)''',line)
                    if mo:
                        groups = mo.groups()
                        # translate section tags
                        pre_tag = groups[0]
                        post_tag = groups[4]
                        if first:
                            if not pre_tag and not post_tag:
                                line = ''
                                break
                            pre.append(pre_tag)
                            pre.append(sec(''.join((groups[1], groups[2], groups[3]))))
                            post_tag = post_tag.lstrip()
                            first = False
                        else:
                            pre.append(pre_tag)
                            pre.append(''.join(('\\', groups[1], groups[2], groups[3])))
                        line = post_tag
                    else:
                        break
                pre.append(line)
                line = ''.join(pre)
                outline(line)

            # skip special marker line
            elif line.startswith(': # script help'):
                continue

            # print code lines as block quote
            else:
                if in_descr:
                    outline()
                    outline("::")
                    outline()
                    in_descr = False
                outline('  {0:03d}  {1}'.format(lineno, line))

# --------------------------------------------------
# |||:sec:||| MAIN
# --------------------------------------------------

##
# Verbosity flag.
_verbose = False

##
# Debug flag.
_debug = False

def main( argv ):               # ||:fnc:||
    """Generic main function.

    :return: exit status
    :param argv: command line arguments (defaults to sys.argv)
    """
    import getopt
    optstr = ""; long_opts = []
    optstr += "h"; long_opts.append( "help" )
    global _verbose
    optstr += "v"; long_opts.append( "verbose" )
    global _debug
    optstr += "d"; long_opts.append( "debug" )
    _opt_test = False
    optstr += "t"; long_opts.append( "test" )
    # |:sec:| options
    try:
        opts, args = getopt.gnu_getopt( argv[ 1: ], optstr, long_opts )
    except getopt.GetoptError as err:
        sys.stderr.write( "".join(( str( err ), "\n" )))
        sys.stderr.write( __doc__ )
        sys.exit(1)
    for opt, arg in opts:
        if opt in ( "-h", "--help" ):
            sys.stdout.write( __doc__ )
            sys.exit()
        # |:sec:| options
        elif opt in ( "-v", "--verbose" ):
            _verbose = True
        elif opt in ( "-d", "--debug" ):
            _verbose = True
            _debug = True
        elif opt in ( "-t", "--test" ):
            _opt_test = True
        else:
            assert False, "unhandled option"
    if _opt_test:
        import doctest
        doctest.testmod( verbose = _verbose )
        sys.exit()
    # |:here:|
    if _debug:
        cmd_line = sys.argv
        sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                dbg_fwid if 'dbg_fwid' in globals() else 15, 'cmd_line',
                cmd_line ))
    del( sys.argv[ 1: ])
    sys.argv.extend( args )
    run()

if __name__ == "__main__":
    sys.argv.insert( 1, '--debug' ) # |:debug:|
    main( sys.argv )
    sys.exit()

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

# :ide: COMPILE: Run with /usr/local/bin/hg-status-all.sh
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " /usr/local/bin/hg-status-all.sh | tee hg-status-all.txt; rst2html.py hg-status-all.txt >hg-status-all.html")))

# :ide: COMPILE: Run with /usr/local/bin/hg-status-all.sh + /home/ws/develop/util/gen-tags/gen_etags.sh
# . (let ((f0 (file-name-nondirectory (buffer-file-name))) (f1 "/usr/local/bin/hg-status-all.sh") (f2 "/home/ws/develop/util/gen-tags/gen_etags.sh") (ob "scripts")) (save-buffer) (compile (concat "python ./" f0 " " f1 " " f2 " | tee " ob ".txt; rst2html.py " ob ".txt >" ob ".html")))

#
# Local Variables:
# mode: python
# comment-start: "#"
# comment-start-skip: "#+"
# comment-column: 0
# End:
