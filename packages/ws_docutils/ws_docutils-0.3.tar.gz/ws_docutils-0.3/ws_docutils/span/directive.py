# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This module has been placed in the public domain.
"""
This module defines the div directive.
"""

__docformat__ = 'reStructuredText'

import sys
import os.path
import re
import time
from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst import Directive, convert_directive_function
from docutils.parsers.rst import directives, roles, states
from docutils.transforms import misc

# --------------------------------------------------
# |||:sec:||| class Div
# --------------------------------------------------

class Div(Directive):
    # ||:cls:||
    """
    Content is included or removed from output based on the format
    argument.

    Content may be parsed by the parser, included as a literal block
    or in raw format.

    Only a part of the text may be included by specifying start and
    end line or text to match before and/or after the text to be used.

    Content may be included inline (content section of directive) or
    imported from a file or url.  The tab-width and encoding of an
    included file or url can be specified.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
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
    has_content = True

    def dbg_data(self, name, data, fmt ='s'): # |:mth:|
        if self.debug_enabled:
            import sys
            fmt_str=''.join(["# {1:<{0}", fmt, "}: [{2!s}]\n"])
            sys.stderr.write(
                fmt_str.format(
                    dbg_fwid if 'dbg_fwid' in globals() else self.debug_fwid,
                    name, data))

    def dbg_mark(self, mark, fmt ='s'): # |:mth:|
        self.dbg_data( '||' ':div:||', mark, fmt)

    def dbg_note(self, note, fmt ='s'): # |:mth:|
        self.dbg_data( ' |' ':div:| ', note, fmt)

    debug_fwid = 15
    debug_enabled = False
    #debug_enabled = True # |:debug:|

    def run(self): # |:mth:|
        if 'debug' in self.options:
            self.debug_enabled = True

        self.dbg_mark('start')

        if (not self.state.document.settings.span_enabled
            or (not self.state.document.settings.file_insertion_enabled
                and ('file' in self.options
                     or 'url' in self.options))):
            raise self.warning('"%s" directive disabled.' % self.name)

        if not nodes.span.ext_initialized:
            nodes.span.ext_init(self.state.inliner.document.settings)

        have_fopt = 'format' in self.options
        have_arg = len(self.arguments) > 0
        if have_fopt and have_arg:
            raise self.error(
                '"{0!s}" directive may not both specify the format as argument '
                'and in the option list.'.format(self.name))

        # check disposition
        if 'literal' in self.options:
            literal = 1
        else:
            literal = 0
        if 'raw' in self.options:
            raw = 1
        else:
            raw = 0
        if literal and raw:
            raise self.error(
                '"{0!s}" directive may not both specify literal '
                'and raw as disposition in the option list.'.format(
                    self.name))
        self.options['literal'] = literal
        self.options['raw'] = raw

        # determine format list
        if have_arg:
            format_ = self.arguments[0]
        elif have_fopt:
            format_ = self.options['format']
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
        self.options['format'] = format_
        self.options['drop'] = drop

        # always remove
        if format_ == '':
            self.dbg_mark('end remove')
            return []

        tab_width = self.options.get(
            'tab-width', self.state.document.settings.tab_width)
        encoding = self.options.get(
            'encoding', self.state.document.settings.input_encoding)

        if 'inline' in self.options:
            inline = 1
        else:
            inline = 0

        # format == '*' == all formats allowed == never remove = keep
        if format_ == "'*'":
            inline = 1

        attributes = self.options

        # |:sec:| get contents
        offset = -1
        source_ = 'direct'
        if self.content:
            if 'file' in self.options or 'url' in self.options:
                raise self.error(
                    '"%s" directive may not both specify an external file '
                    'and have content.' % self.name)
            text = '\n'.join(self.content)
            offset = self.content_offset
        elif 'file' in self.options:
            if 'url' in self.options:
                raise self.error(
                    'The "file" and "url" options may not be simultaneously '
                    'specified for the "%s" directive.' % self.name)
            source_dir = os.path.dirname(
                os.path.abspath(self.state.document.current_source))
            path = os.path.normpath(os.path.join(source_dir,
                                                 self.options['file']))
            path = utils.relative_path(None, path)
            try:
                self.state.document.settings.record_dependencies.add(path)
                raw_file = io.FileInput(
                    source_path=path, encoding=encoding,
                    error_handler=(self.state.document.settings.\
                                   input_encoding_error_handler),
                    handle_io_errors=None)
            except IOError, error:
                raise self.severe('Problems with "%s" directive path:\n%s.'
                                  % (self.name, error))
            try:
                text = raw_file.read()
            except UnicodeError, error:
                raise self.severe(
                    'Problem with "%s" directive:\n%s: %s'
                    % (self.name, error.__class__.__name__, error))
            attributes['source'] = path
            source_ = path
        elif 'url' in self.options:
            source = self.options['url']
            # Do not import urllib2 at the top of the module because
            # it may fail due to broken SSL dependencies, and it takes
            # about 0.15 seconds to load.
            import urllib2
            try:
                raw_text = urllib2.urlopen(source).read()
            except (urllib2.URLError, IOError, OSError), error:
                raise self.severe(
                    'Problems with "%s" directive URL "%s":\n%s.'
                    % (self.name, self.options['url'], error))
            raw_file = io.StringInput(
                source=raw_text, source_path=source, encoding=encoding,
                error_handler=(self.state.document.settings.\
                               input_encoding_error_handler))
            try:
                text = raw_file.read()
            except UnicodeError, error:
                raise self.severe(
                    'Problem with "%s" directive:\n%s: %s'
                    % (self.name, error.__class__.__name__, error))
            attributes['source'] = source
            source_ = source
        else:
            # This will always fail because there is no content.
            self.assert_has_content()

        # |:sec:| extract lines
        startline = self.options.get('start-line', None)
        endline = self.options.get('end-line', None)
        try:
            if startline or (endline is not None):
                lines = statemachine.string2lines(
                    text, tab_width, convert_whitespace=1)
                text = '\n'.join(lines[startline:endline])
        except UnicodeError, error:
            raise self.severe(
                'Problem with "%s" directive:\n%s: %s'
                % (self.name, error.__class__.__name__, error))
        # start-after/end-before: no restrictions on newlines in match-text,
        # and no restrictions on matching inside lines vs. line boundaries

        after_text = self.options.get('start-after', None)
        if after_text:
            opttext_nodes, opttext_msgs = self.state.inline_text(after_text,offset)
            if len(opttext_msgs) > 0:
                self.dbg_mark('end error')
                return opttext_nodes, opttext_msgs
            opttext_txt = []
            for otn in opttext_nodes:
                opttext_txt.append( otn.astext())
            after_text = ''.join(opttext_txt)
            # skip content in rawtext before *and incl.* a matching text
            after_index = text.find(after_text)
            if after_index < 0:
                raise self.severe(
                    'Problem with "start-after" option of "{0!s}" '
                    'directive:\nText `{1!s}` not found.'.format(
                        self.name,after_text))
            text = text[after_index + len(after_text):]
        before_text = self.options.get('end-before', None)
        if before_text:
            opttext_nodes, opttext_msgs = self.state.inline_text(before_text,offset)
            if len(opttext_msgs) > 0:
                self.dbg_mark('end error')
                return opttext_nodes, opttext_msgs
            opttext_txt = []
            for otn in opttext_nodes:
                opttext_txt.append( otn.astext())
            before_text = ''.join(opttext_txt)
            # skip content in rawtext after *and incl.* a matching text
            before_index = text.find(before_text)
            if before_index < 0:
                raise self.severe(
                    'Problem with "end-before" option of "{0!s}" '
                    'directive:\nText `{1!s}` not found.'.format(
                        self.name,before_text))
            text = text[:before_index]

        # |:sec:| disposition
        if literal:
            # Literal Block
            raw_text = text
            if tab_width >= 0:
                text = raw_text.expandtabs(tab_width)
            literal_block = nodes.literal_block(raw_text, text)
            literal_block.line = 1
            div_node = nodes.div('', literal_block, **attributes)
        elif raw:
            # Raw Text
            raw_node = nodes.raw('', text, **attributes)
            div_node = nodes.div('', raw_node, **attributes)
        else:
            # Parse Text
            if inline:
                include_lines = statemachine.string2lines(
                    text, tab_width, convert_whitespace=1)
                self.state_machine.insert_input(include_lines, source_)
                self.dbg_mark('end inline parse')
                return []

            content = statemachine.StringList(
                statemachine.string2lines(
                    text, tab_width, convert_whitespace=1),
                source=source_)

            div_node = nodes.div('', *[], **attributes)
            self.state.nested_parse(content, offset, div_node)
        if inline:
            self.dbg_mark('end inline')
            return div_node.children
        self.dbg_mark('end')
        return [div_node]

# --------------------------------------------------
# |||:sec:||| class DivX
# --------------------------------------------------

class DivX(Div):
    # ||:cls:||
    """
    Debugging class for Div.
    """

    def run(self): # |:mth:|
        self.options['debug'] = True
        try:
            del(self.options['inline'])
        except KeyError:
            pass
        return Div.run(self)

        import sys # |:debug:|
        sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                dbg_fwid if 'dbg_fwid' in globals() else 15,
                '||:div:||', 'start' ))
        if False:
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '---------------', '--------------------------------------------------' ))
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    self.__class__.__name__ + '.dir', dir(self)))
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '---------------', '--------------------------------------------------' ))
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    self.state.__class__.__name__ + '.dir', dir(self.state)))
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '---------------', '--------------------------------------------------' ))
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    self.state.parent.__class__.__name__ + '.dir', dir(self.state.parent)))

        if (not self.state.document.settings.span_enabled
            or (not self.state.document.settings.file_insertion_enabled
                and ('file' in self.options
                     or 'url' in self.options))):
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
            raise self.warning('"%s" directive disabled.' % self.name)

        if not nodes.span.ext_initialized:
            nodes.span.ext_init(self.state.inliner.document.settings)

        # |:sec:| check format list
        have_fopt = 'format' in self.options
        have_arg = len(self.arguments) > 0
        if have_fopt and have_arg:
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
            raise self.error(
                '"{0!s}" directive may not both specify the format as argument '
                'and in the option list.'.format(self.name))

        # check disposition
        if 'literal' in self.options:
            literal = 1
        else:
            literal = 0
        if 'raw' in self.options:
            raw = 1
        else:
            raw = 0
        if literal and raw:
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
            raise self.error(
                '"{0!s}" directive may not both specify literal '
                'and raw as disposition in the option list.'.format(
                    self.name))
        self.options['literal'] = literal
        self.options['raw'] = raw

        # determine format list
        if have_arg:
            format_ = self.arguments[0]
        elif have_fopt:
            format_ = self.options['format']
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
        self.options['format'] = format_
        self.options['drop'] = drop

        # always remove
        if format_ == '':
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'end' ))
            return []
        # format == '*' == all formats allowed == never remove = keep
        if format_ == "'*'":
            wrap = True # |:check:| let's always wrap?
        else:
            wrap = True

        tab_width = self.options.get(
            'tab-width', self.state.document.settings.tab_width)
        encoding = self.options.get(
            'encoding', self.state.document.settings.input_encoding)

        if 'inline' in self.options:
            inline = 1
        else:
            inline = 0

        attributes = self.options

        # |:sec:| get contents
        offset = -1
        source_ = 'direct'
        if self.content:
            if 'file' in self.options or 'url' in self.options:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                raise self.error(
                    '"%s" directive may not both specify an external file '
                    'and have content.' % self.name)
            text = '\n'.join(self.content)
            offset = self.content_offset
        elif 'file' in self.options:
            if 'url' in self.options:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                raise self.error(
                    'The "file" and "url" options may not be simultaneously '
                    'specified for the "%s" directive.' % self.name)
            source_dir = os.path.dirname(
                os.path.abspath(self.state.document.current_source))
            path = os.path.normpath(os.path.join(source_dir,
                                                 self.options['file']))
            path = utils.relative_path(None, path)
            try:
                self.state.document.settings.record_dependencies.add(path)
                raw_file = io.FileInput(
                    source_path=path, encoding=encoding,
                    error_handler=(self.state.document.settings.\
                                   input_encoding_error_handler),
                    handle_io_errors=None)
            except IOError, error:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                raise self.severe('Problems with "%s" directive path:\n%s.'
                                  % (self.name, error))
            try:
                text = raw_file.read()
            except UnicodeError, error:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                raise self.severe(
                    'Problem with "%s" directive:\n%s: %s'
                    % (self.name, error.__class__.__name__, error))
            attributes['source'] = path
            source_ = path
        elif 'url' in self.options:
            source = self.options['url']
            # Do not import urllib2 at the top of the module because
            # it may fail due to broken SSL dependencies, and it takes
            # about 0.15 seconds to load.
            import urllib2
            try:
                raw_text = urllib2.urlopen(source).read()
            except (urllib2.URLError, IOError, OSError), error:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                raise self.severe(
                    'Problems with "%s" directive URL "%s":\n%s.'
                    % (self.name, self.options['url'], error))
            raw_file = io.StringInput(
                source=raw_text, source_path=source, encoding=encoding,
                error_handler=(self.state.document.settings.\
                               input_encoding_error_handler))
            try:
                text = raw_file.read()
            except UnicodeError, error:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                raise self.severe(
                    'Problem with "%s" directive:\n%s: %s'
                    % (self.name, error.__class__.__name__, error))
            attributes['source'] = source
            source_ = source
        else:
            # This will always fail because there is no content.
            self.assert_has_content()

        # |:sec:| extract lines
        startline = self.options.get('start-line', None)
        endline = self.options.get('end-line', None)
        try:
            if startline or (endline is not None):
                lines = statemachine.string2lines(
                    text, tab_width, convert_whitespace=1)
                text = '\n'.join(lines[startline:endline])
        except UnicodeError, error:
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
            raise self.severe(
                'Problem with "%s" directive:\n%s: %s'
                % (self.name, error.__class__.__name__, error))
        # start-after/end-before: no restrictions on newlines in match-text,
        # and no restrictions on matching inside lines vs. line boundaries

        after_text = self.options.get('start-after', None)
        if after_text:
            opttext_nodes, opttext_msgs = self.state.inline_text(after_text,offset)
            if len(opttext_msgs) > 0:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                return opttext_nodes, opttext_msgs
            opttext_txt = []
            for otn in opttext_nodes:
                opttext_txt.append( otn.astext())
            after_text = ''.join(opttext_txt)
            # skip content in rawtext before *and incl.* a matching text
            after_index = text.find(after_text)
            if after_index < 0:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                raise self.severe(
                    'Problem with "start-after" option of "{0!s}" '
                    'directive:\nText `{1!s}` not found.'.format(
                        self.name,after_text))
            text = text[after_index + len(after_text):]
        before_text = self.options.get('end-before', None)
        if before_text:
            opttext_nodes, opttext_msgs = self.state.inline_text(before_text,offset)
            if len(opttext_msgs) > 0:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                return opttext_nodes, opttext_msgs
            opttext_txt = []
            for otn in opttext_nodes:
                opttext_txt.append( otn.astext())
            before_text = ''.join(opttext_txt)
            # skip content in rawtext after *and incl.* a matching text
            before_index = text.find(before_text)
            if before_index < 0:
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'error' ))
                raise self.severe(
                    'Problem with "end-before" option of "{0!s}" '
                    'directive:\nText `{1!s}` not found.'.format(
                        self.name,before_text))
            text = text[:before_index]

        # |:sec:| disposition
        if literal:
            # Literal Block
            raw_text = text
            if tab_width >= 0:
                text = raw_text.expandtabs(tab_width)
            literal_block = nodes.literal_block(raw_text, text)
            literal_block.line = 1
            if not wrap:
                div_node = literal_block
            else:
                div_node = nodes.div('', literal_block, **attributes)
        elif raw:
            # Raw Text
            raw_node = nodes.raw('', text, **attributes)
            div_node = nodes.div('', raw_node, **attributes)
        else:
            # Parse Text
            parent = self.state.parent
            pchild_ct = len(parent.children)
            # |:debug:|
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    'pname', parent.__class__.__name__ ))
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    'pchild_ct', pchild_ct ))
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    'state', self.state.__class__.__name__ ))
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    'state.nested_sm', self.state.nested_sm.__name__ ))
            # sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
            #         dbg_fwid if 'dbg_fwid' in globals() else 15,
            #         'state dir', dir(self.state)))

            if inline and 0:
                include_lines = statemachine.string2lines(
                    text, tab_width, convert_whitespace=1)
                self.state_machine.insert_input(include_lines, source_)
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'end' ))
                return []

            content = statemachine.StringList(
                statemachine.string2lines(
                    text, tab_width, convert_whitespace=1),
                source=source_)

            div_node = nodes.div('', *[], **attributes)
            try:
                self.state.nested_parse(content, offset, div_node, 1)
            except Exception as e:
                sys.stderr.write( "# {1:<{0}s}: [{2!r}]\n".format(
                        dbg_fwid if 'dbg_fwid' in globals() else 15,
                        e.__class__.__name__, dir(e)))
                sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                        dbg_fwid if 'dbg_fwid' in globals() else 15,
                        '||:div:||', 'error below' ))
                raise e
            sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    'children', div_node.children ))

        if inline and 0:
            return div_node.children
        sys.stderr.write( "# {1:<{0}s}: [{2!s}]\n".format(
                    dbg_fwid if 'dbg_fwid' in globals() else 15,
                    '||:div:||', 'end' ))
        return [div_node]

# --------------------------------------------------
# |||:sec:||| Register Div
# --------------------------------------------------

_register_div_class = Div
#_register_div_class = DivX # |:debug:|

# Register as if part of docutils.

# add role name to language en
from docutils.parsers.rst.languages import en
en.directives['div']  = 'div'
# install `div` directive
import docutils.parsers.rst.directives
import docutils.parsers.rst.directives.misc
docutils.parsers.rst.directives.misc.Div = _register_div_class
docutils.parsers.rst.directives._directive_registry[ 'div' ] = ('misc', _register_div_class.__name__)

# --------------------------------------------------
# |||:sec:||| Register DivX
# --------------------------------------------------

# Register as if part of docutils.

# add role name to language en
from docutils.parsers.rst.languages import en
en.directives['divx']  = 'divx'
# install `divx` directive
import docutils.parsers.rst.directives
import docutils.parsers.rst.directives.misc
docutils.parsers.rst.directives.misc.DivX = DivX
docutils.parsers.rst.directives._directive_registry[ 'divx' ] = ('misc', 'DivX')

# Register application specific.

#import docutils.parsers.rst.directives
#docutils.parsers.rst.directives.register_directive('div', Div)

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
