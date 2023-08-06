# Copyright (C) 2010-2012 W. Trevor King <wking@drexel.edu>
#
# This file is part of Hooke.
#
# Hooke is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Hooke is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hooke.  If not, see <http://www.gnu.org/licenses/>.

"""Defines :class:`CommandLine` for driving Hooke from the command
line.
"""

import codecs
import cmd
import logging
import optparse
import pprint
try:
    import readline # including readline makes cmd.Cmd.cmdloop() smarter
except ImportError, e:
    import logging
    logging.warn('could not import readline, bash-like line editing disabled.')
import shlex
import sys

from ..command import CommandExit, Exit, Command, Argument, StoreValue
from ..engine import CommandMessage, CloseEngine
from ..interaction import EOFResponse, Request, ReloadUserInterfaceConfig
from ..ui import UserInterface
from ..util.convert import from_string
from ..util.encoding import get_input_encoding, get_output_encoding


# Define a few helper classes.

class EOF (EOFError):
    """Raise upon reaching the end of the input file.

    After this point, no more user interaction is possible.
    """
    pass

class Default (object):
    """Marker for options not given on the command line.
    """
    pass

class CommandLineParser (optparse.OptionParser):
    """Implement a command line syntax for a
    :class:`hooke.command.Command`.
    """
    def __init__(self, command, name_fn):
        optparse.OptionParser.__init__(self, prog=name_fn(command.name))
        self.command = command
        self.command_opts = []
        self.command_args = []
        for a in command.arguments:
            if a.name == 'help':
                continue # 'help' is a default OptionParser option
            if a.optional == True:
                name = name_fn(a.name)
                type = a.type
                if type == 'bool':
                    if a.default == True:
                        try:
                            self.add_option(
                                '--disable-%s' % name, dest=name,
                                default=Default, action='store_false',
                                help=self._argument_help(a))
                        except optparse.OptionConflictError, e:
                            logging.warn('error in %s: %s' % (command, e))
                            raise
                        self.command_opts.append(a)
                        continue
                    elif a.default == False:
                        try:
                            self.add_option(
                                '--enable-%s' % name, dest=name,
                                default=Default, action='store_true',
                                help=self._argument_help(a))
                        except optparse.OptionConflictError, e:
                            logging.warn('error in %s: %s' % (command, e))
                            raise
                        self.command_opts.append(a)
                        continue
                    else:
                        type = 'string'
                elif type not in ['string', 'int', 'long', 'choice', 'float',
                                  'complex']:
                    type = 'string'
                try:
                    self.add_option(
                        '--%s' % name, dest=name, type=type, default=Default,
                        help=self._argument_help(a))
                except optparse.OptionConflictError, e:
                    logging.warn('error in %s: %s' % (command, e))
                    raise
                self.command_opts.append(a)
            else:
                self.command_args.append(a)
        infinite_counters = [a for a in self.command_args if a.count == -1]
        assert len(infinite_counters) <= 1, \
            'Multiple infinite counts for %s: %s\nNeed a better CommandLineParser implementation.' \
            % (command.name, ', '.join([a.name for a in infinite_counters]))
        if len(infinite_counters) == 1: # move the big counter to the end.
            infinite_counter = infinite_counters[0]
            self.command_args.remove(infinite_counter)
            self.command_args.append(infinite_counter)

    def _argument_help(self, argument):
        return '%s (%s)' % (argument._help, argument.default)
        # default in the case of callbacks, config-backed values, etc.?

    def exit(self, status=0, msg=None):
        """Override :meth:`optparse.OptionParser.exit` which calls
        :func:`sys.exit`.
        """
        if msg:
            raise optparse.OptParseError(msg)
        raise optparse.OptParseError('OptParse EXIT')

class CommandMethod (object):
    """Base class for method replacer.

    The .__call__ methods of `CommandMethod` subclasses functions will
    provide the `do_*`, `help_*`, and `complete_*` methods of
    :class:`HookeCmd`.
    """
    def __init__(self, cmd, command, name_fn):
        self.cmd = cmd
        self.command = command
        self.name_fn = name_fn

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

class DoCommand (CommandMethod):
    def __init__(self, *args, **kwargs):
        super(DoCommand, self).__init__(*args, **kwargs)
        self.parser = CommandLineParser(self.command, self.name_fn)

    def __call__(self, args):
        try:
            args = self._parse_args(args)
        except optparse.OptParseError, e:
            self.cmd.stdout.write(unicode(e).lstrip()+'\n')
            self.cmd.stdout.write('Failure\n')
            return
        cm = CommandMessage(self.command.name, args)
        self.cmd.ui._submit_command(cm, self.cmd.inqueue)
        while True:
            msg = self.cmd.outqueue.get()
            if isinstance(msg, Exit):
                return True
            elif isinstance(msg, CommandExit):
                self.cmd.stdout.write(msg.__class__.__name__+'\n')
                self.cmd.stdout.write(unicode(msg).rstrip()+'\n')
                break
            elif isinstance(msg, ReloadUserInterfaceConfig):
                self.cmd.ui.reload_config(msg.config)
                continue
            elif isinstance(msg, Request):
                try:
                    self._handle_request(msg)
                except EOF:
                    return True
                continue
            if isinstance(msg, dict):
                text = pprint.pformat(msg)
            else:
                text = unicode(msg)
            self.cmd.stdout.write(text.rstrip()+'\n')

    def _parse_args(self, args):
        options,args = self.parser.parse_args(args)
        self._check_argument_length_bounds(args)
        params = {}
        for argument in self.parser.command_opts:
            value = getattr(options, self.name_fn(argument.name))
            if value != Default:
                params[argument.name] = value
        arg_index = 0
        for argument in self.parser.command_args:
            if argument.count == 1:
                params[argument.name] = from_string(args[arg_index],
                                                    argument.type)
            elif argument.count > 1:
                params[argument.name] = [
                    from_string(a, argument.type)
                    for a in args[arg_index:arg_index+argument.count]]
            else: # argument.count == -1:
                params[argument.name] = [
                    from_string(a, argument.type) for a in args[arg_index:]]
            arg_index += argument.count
        return params

    def _check_argument_length_bounds(self, arguments):
        """Check that there are an appropriate number of arguments in
        `args`.

        If not, raise optparse.OptParseError().
        """
        min_args = 0
        max_args = 0
        for argument in self.parser.command_args:
            if argument.optional == False and argument.count > 0:
                min_args += argument.count
            if max_args >= 0: # otherwise already infinite
                if argument.count == -1:
                    max_args = -1
                else:
                    max_args += argument.count
        if len(arguments) < min_args \
                or (max_args >= 0 and len(arguments) > max_args):
            if min_args == max_args:
                target_string = str(min_args)
            elif max_args == -1:
                target_string = 'more than %d' % min_args
            else:
                target_string = '%d to %d' % (min_args, max_args)
            raise optparse.OptParseError(
                '%d arguments given, but %s takes %s'
                % (len(arguments), self.name_fn(self.command.name),
                   target_string))

    def _handle_request(self, msg):
        """Repeatedly try to get a response to `msg`.
        """
        prompt = getattr(self, '_%s_request_prompt' % msg.type, None)
        if prompt == None:
            raise NotImplementedError('_%s_request_prompt' % msg.type)
        prompt_string = prompt(msg)
        parser = getattr(self, '_%s_request_parser' % msg.type, None)
        if parser == None:
            raise NotImplementedError('_%s_request_parser' % msg.type)
        error = None
        while True:
            if error != None:
                self.cmd.stdout.write(''.join([
                        error.__class__.__name__, ': ', unicode(error), '\n']))
            self.cmd.stdout.write(prompt_string)
            stdin = sys.stdin
            try:
                sys.stdin = self.cmd.stdin
                raw_response = raw_input()
            except EOFError, e:
                self.cmd.inqueue.put(EOFResponse())
                self.cmd.inqueue.put(CloseEngine())
                raise EOF
            finally:
                sys.stdin = stdin
            value = parser(msg, raw_response)
            try:
                response = msg.response(value)
                break
            except ValueError, error:
                continue
        self.cmd.inqueue.put(response)

    def _boolean_request_prompt(self, msg):
        if msg.default == True:
            yn = ' [Y/n] '
        else:
            yn = ' [y/N] '
        return msg.msg + yn

    def _boolean_request_parser(self, msg, response):
        value = response.strip().lower()
        if value.startswith('y'):
            value = True
        elif value.startswith('n'):
            value = False
        elif len(value) == 0:
            value = msg.default
        return value

    def _string_request_prompt(self, msg):
        if msg.default == None:
            d = ' '
        else:
            d = ' [%s] ' % msg.default
        return msg.msg + d

    def _string_request_parser(self, msg, response):
        response = response.strip()
        if response == '':
            return msg.default
        return response.strip()

    def _float_request_prompt(self, msg):
        return self._string_request_prompt(msg)

    def _float_request_parser(self, msg, resposne):
        if response.strip() == '':
            return msg.default
        return float(response)

    def _selection_request_prompt(self, msg):
        options = []
        for i,option in enumerate(msg.options):
            options.append('   %d) %s' % (i,option))
        options = ''.join(options)
        if msg.default == None:
            prompt = '? '
        else:
            prompt = '? [%d] ' % msg.default
        return '\n'.join([msg.msg,options,prompt])
    
    def _selection_request_parser(self, msg, response):
        if response.strip() == '':
            return msg.default
        return int(response)

    def _point_request_prompt(self, msg):
        block = msg.curve.data[msg.block]
        block_info = ('(curve: %s, block: %s, %d points)'
                      % (msg.curve.name,
                         block.info['name'],
                         block.shape[0]))

        if msg.default == None:
            prompt = '? '
        else:
            prompt = '? [%d] ' % msg.default
        return ' '.join([msg.msg,block_info,prompt])
    
    def _point_request_parser(self, msg, response):
        if response.strip() == '':
            return msg.default
        return int(response)


class HelpCommand (CommandMethod):
    """Supersedes :class:`hooke.plugin.engine.HelpCommand`.
    """
    def __init__(self, *args, **kwargs):
        super(HelpCommand, self).__init__(*args, **kwargs)
        self.parser = CommandLineParser(self.command, self.name_fn)

    def __call__(self):
        blocks = [self.parser.format_help(),
                  self._command_message(),
                  '----',
                  'Usage: ' + self._usage_string(),
                  '']
        self.cmd.stdout.write('\n'.join(blocks))

    def _command_message(self):
        return self.command._help

    def _usage_string(self):
        if len(self.parser.command_opts) == 0:
            options_string = ''
        else:
            options_string = '[options]'
        arg_string = ' '.join(
            [self.name_fn(arg.name) for arg in self.parser.command_args])
        return ' '.join([x for x in [self.parser.prog,
                                     options_string,
                                     arg_string]
                         if x != ''])

class CompleteCommand (CommandMethod):
    def __call__(self, text, line, begidx, endidx):
        pass



# Now onto the main attraction.

class HookeCmd (cmd.Cmd):
    def __init__(self, ui, commands, inqueue, outqueue):
        cmd.Cmd.__init__(self)
        self.ui = ui
        self.commands = commands
        self.prompt = 'hooke> '
        self._add_command_methods()
        self.inqueue = inqueue
        self.outqueue = outqueue

    def _name_fn(self, name):
        return name.replace(' ', '_')

    def _add_command_methods(self):
        for command in self.commands:
            if command.name == 'exit':
                command.aliases.extend(['quit', 'EOF'])
            for name in [command.name] + command.aliases:
                name = self._name_fn(name)
                setattr(self.__class__, 'help_%s' % name,
                        HelpCommand(self, command, self._name_fn))
                if name != 'help':
                    setattr(self.__class__, 'do_%s' % name,
                            DoCommand(self, command, self._name_fn))
                    setattr(self.__class__, 'complete_%s' % name,
                            CompleteCommand(self, command, self._name_fn))

    def parseline(self, line):
        """Override Cmd.parseline to use shlex.split.

        Notes
        -----
        This allows us to handle comments cleanly.  With the default
        Cmd implementation, a pure comment line will call the .default
        error message.

        Since we use shlex to strip comments, we return a list of
        split arguments rather than the raw argument string.
        """
        line = line.strip()
        argv = shlex.split(line, comments=True, posix=True)
        if len(argv) == 0:
            return None, None, '' # return an empty line
        cmd = argv[0]
        args = argv[1:]
        if cmd == '?':
            cmd = 'help'
        elif cmd == '!':
            cmd = 'system'
        return cmd, args, line

    def do_help(self, arg):
        """Wrap Cmd.do_help to handle our .parseline argument list.
        """
        if len(arg) == 0:
            return cmd.Cmd.do_help(self, '')
        return cmd.Cmd.do_help(self, arg[0])

    def emptyline(self):
        """Override Cmd.emptyline to not do anything.

        Repeating the last non-empty command seems unwise.  Explicit
        is better than implicit.
        """
        pass


class CommandLine (UserInterface):
    """Command line interface.  Simple and powerful.
    """
    def __init__(self):
        super(CommandLine, self).__init__(name='command line')

    def _cmd(self, commands, ui_to_command_queue, command_to_ui_queue):
        cmd = HookeCmd(self, commands,
                       inqueue=ui_to_command_queue,
                       outqueue=command_to_ui_queue)
        #cmd.stdin = codecs.getreader(get_input_encoding())(cmd.stdin)
        cmd.stdout = codecs.getwriter(get_output_encoding())(cmd.stdout)
        return cmd

    def run(self, commands, ui_to_command_queue, command_to_ui_queue):
        cmd = self._cmd(commands, ui_to_command_queue, command_to_ui_queue)
        cmd.cmdloop(self._splash_text(extra_info={
                    'get-details':'run `license`',
                    }))

    def run_lines(self, commands, ui_to_command_queue, command_to_ui_queue,
                  lines):
        cmd = self._cmd(commands, ui_to_command_queue, command_to_ui_queue)
        for line in lines:
            cmd.onecmd(line)
