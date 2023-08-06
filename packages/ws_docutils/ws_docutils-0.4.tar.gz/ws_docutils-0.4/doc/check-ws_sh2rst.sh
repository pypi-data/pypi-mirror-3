#!/bin/sh
#
# check-ws_sh2rst.sh - convert myself to ReST with ws_sh2rst.py
#
# usage: check-ws_sh2rst.sh [OPTIONS]
#
# OPTIONS
#   -h, --help  show usage
#   --docu      show full documentation
#
# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This program has been placed in the public domain.
#
:  # script help

# --------------------------------------------------
# |||:sec:||| FUNCTIONS
# --------------------------------------------------

# Here, **the script** examines itself to *provide* help.
usage ()
{
    script_help="script-help"
    ( "${script_help}" ${1+"$@"} "${0}" ) 2>/dev/null \
    || ${SED__PROG-sed} -n '3,/^[^#]/{;/^[^#]/d;p;}' "${0}";
}

# A minimal option handler, to *provide* basic help.
test x"${1+set}" = xset && \
case "${1}" in
-\?|-h|--help) usage; exit 0;;
--docu) usage --full; exit 0;;
esac

# --------------------------------------------------
# |||:sec:||| MAIN
# --------------------------------------------------

# |:here:| tags like \|:here:\| are recognized and commented out in the output

# Call `ws_sh2rst.py` to produce ReST output of **this script**.
../tools/ws_sh2rst.py "${0}"

# |:todo:| add a little more beef ...

exit # |||:here:|||

#
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' (eIDE-menu "z")

# :ide: SNIP: insert OPTION LOOP
# . (snip-insert-mode "sh_b.opt-loop" nil t)

# :ide: SHELL: Run with --docu
# . (progn (save-buffer) (shell-command (concat "sh " (file-name-nondirectory (buffer-file-name)) " --docu")))

# :ide: SHELL: Run with --help
# . (progn (save-buffer) (shell-command (concat "sh " (file-name-nondirectory (buffer-file-name)) " --help")))

# :ide: SHELL: Run w/o args
# . (progn (save-buffer) (shell-command (concat "sh " (file-name-nondirectory (buffer-file-name)) " ")))

#
# Local Variables:
# mode: sh
# comment-start: "#"
# comment-start-skip: "#+"
# comment-column: 0
# End:
# mmm-classes: (here-doc ide-entries)
