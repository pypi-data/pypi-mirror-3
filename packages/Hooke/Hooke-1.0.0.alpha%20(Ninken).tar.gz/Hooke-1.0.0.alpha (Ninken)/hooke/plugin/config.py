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

"""The `config` module provides :class:`ConfigPlugin` and several
associated :class:`hooke.command.Command`\s for handling
:mod:`hooke.config` classes.
"""

import os.path
from StringIO import StringIO

from ..command import Command, Argument, Failure
from ..interaction import ReloadUserInterfaceConfig
from . import Builtin


class ConfigPlugin (Builtin):
    def __init__(self):
        super(ConfigPlugin, self).__init__(name='config')
        self._commands = [GetCommand(self), SetCommand(self),
                          PrintCommand(self), SaveCommand(self),]


# Define common or complicated arguments

SectionArgument = Argument(
    name='section', type='string', optional=False,
    help="""
Configuration section to act on.
""".strip())

OptionArgument = Argument(
    name='option', type='string', optional=False,
    help="""
Configuration option to act on.
""".strip())


# Define commands

class GetCommand (Command):
    """Get the current value of a configuration option.
    """
    def __init__(self, plugin):
        super(GetCommand, self).__init__(
            name='get config',
            arguments=[SectionArgument, OptionArgument],
            help=self.__doc__, plugin=plugin)

    def _run(self, hooke, inqueue, outqueue, params):
	outqueue.put(hooke.config.get(params['section'], params['option']))

class SetCommand (Command):
    """Set the current value of a configuration option.

    Currently many config options are read at startup time, and config
    dicts are passed out to their target classes.  This means that changes
    to the central :attr:`hooke.hooke.Hooke.config` location *will not* be
    noticed by the target classes unless the configuration is reloaded.
    This reloading may cause problems in poorly written UIs.
    """
    def __init__(self, plugin):
        super(SetCommand, self).__init__(
            name='set config',
            arguments=[
                SectionArgument, OptionArgument,
                Argument(
                    name='value', type='string', optional=False,
                    help='Value to set.'),
                ],
            help=self.__doc__, plugin=plugin)

    def _run(self, hooke, inqueue, outqueue, params):
	hooke.config.set(params['section'], params['option'], params['value'])
        # push config changes
        hooke.load_log()
        hooke.configure_plugins()
        hooke.configure_drivers()
        hooke.configure_ui()  # for post-HookeRunner Hooke return.
        # notify UI to update config
        outqueue.put(ReloadUserInterfaceConfig(hooke.config))

class PrintCommand (Command):
    """Get the current configuration file text.
    """
    def __init__(self, plugin):
        super(PrintCommand, self).__init__(
            name='print config', help=self.__doc__, plugin=plugin)

    def _run(self, hooke, inqueue, outqueue, params):
        out = StringIO()
        hooke.config.write(out)
        outqueue.put(out.getvalue())


class SaveCommand (Command):
    """Save the current configuration options.
    """
    def __init__(self, plugin):
        super(SaveCommand, self).__init__(
            name='save config',
            arguments=[
                Argument(name='output', type='file',
                         help="""
File name for the output configuration.  Defaults to overwriting the
most local loaded config file.
""".strip()),
                ],
            help=self.__doc__, plugin=plugin)

    def _run(self, hooke, inqueue, outqueue, params):
        f = None
        try:
            if params['output'] != None:
                f = open(os.path.expanduser(params['output']), 'w')
            hooke.config.write(fp=f)
        finally:
            if f != None:
                f.close()
