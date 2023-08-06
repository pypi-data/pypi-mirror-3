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

"""Defines :class:`GUI` providing a wxWidgets interface to Hooke.

We only define the :class:`UserInterface` here, to minimize required
dependencies for users who may not wish to use this interface.  The
bulk of the interface is defined in :mod:`interface`.
"""

import os.path as _os_path

from ...ui import UserInterface as _UserInterface
from ...config import Setting as _Setting
try:
    import wxversion as _wxversion
except ImportError, e:
    _wxversion = None
    _wxversion_error = e
else:
    try:
        from .interface import HookeApp as _HookeApp
    except _wxversion.VersionError, e:
        _wxversion = None
        _wxversion_error = e

class GUI (_UserInterface):
    """wxWindows graphical user interface.
    """
    def __init__(self):
        super(GUI, self).__init__(name='gui')

    def default_settings(self):
        """Return a list of :class:`hooke.config.Setting`\s for any
        configurable UI settings.

        The suggested section setting is::

            Setting(section=self.setting_section, help=self.__doc__)
        """
        return [
            _Setting(section=self.setting_section, help=self.__doc__),
            _Setting(section=self.setting_section, option='icon image',
                     value=_os_path.join('doc', 'img', 'microscope.ico'),
                     type='file',
                     help='Path to the hooke icon image.'),
            _Setting(section=self.setting_section, option='show splash screen',
                     value=True, type='bool',
                     help='Enable/disable the splash screen'),
            _Setting(section=self.setting_section, option='splash screen image',
                     value=_os_path.join('doc', 'img', 'hooke.jpg'),
                     type='file',
                     help='Path to the Hooke splash screen image.'),
            _Setting(section=self.setting_section,
                     option='splash screen duration',
                     value=1000, type='int',
                     help='Duration of the splash screen in milliseconds.'),
            _Setting(section=self.setting_section, option='perspective path',
                     value=_os_path.join('resources', 'gui', 'perspective'),
                     help='Directory containing perspective files.'), # TODO: allow colon separated list, like $PATH.
            _Setting(section=self.setting_section, option='perspective extension',
                     value='.txt',
                     help='Extension for perspective files.'),
            _Setting(section=self.setting_section, option='hide extensions',
                     value=False, type='bool',
                     help='Hide file extensions when displaying names.'),
            _Setting(section=self.setting_section, option='plot legend',
                     value=True, type='bool',
                     help='Enable/disable the plot legend.'),
            _Setting(section=self.setting_section, option='plot SI format',
                     value='True', type='bool',
                     help='Enable/disable SI plot axes numbering.'),
            _Setting(section=self.setting_section, option='plot decimals',
                     value=2, type='int',
                     help=('Number of decimal places to show if "plot SI '
                           'format" is enabled.')),
            _Setting(section=self.setting_section, option='folders-workdir',
                     value='.', type='path',
                     help='This should probably go...'),
            _Setting(section=self.setting_section, option='folders-filters',
                     value='.', type='path',
                     help='This should probably go...'),
            _Setting(section=self.setting_section, option='active perspective',
                     value='Default',
                     help='Name of active perspective file (or "Default").'),
            _Setting(section=self.setting_section,
                     option='folders-filter-index',
                     value=0, type='int',
                     help='This should probably go...'),
            _Setting(section=self.setting_section, option='main height',
                     value=450, type='int',
                     help='Height of main window in pixels.'),
            _Setting(section=self.setting_section, option='main width',
                     value=800, type='int',
                     help='Width of main window in pixels.'),
            _Setting(section=self.setting_section, option='main top',
                     value=0, type='int',
                     help='Pixels from screen top to top of main window.'),
            _Setting(section=self.setting_section, option='main left',
                     value=0, type='int',
                     help='Pixels from screen left to left of main window.'),
            _Setting(section=self.setting_section, option='selected command',
                     value='load playlist',
                     help='Name of the initially selected command.'),
            ]

    def _app(self, commands, ui_to_command_queue, command_to_ui_queue):
        if _wxversion is None:
            raise _wxversion_error
        redirect = True
        if __debug__:
            redirect=False
        app = _HookeApp(gui=self,
                       commands=commands,
                       inqueue=ui_to_command_queue,
                       outqueue=command_to_ui_queue,
                       redirect=redirect)
        return app

    def run(self, commands, ui_to_command_queue, command_to_ui_queue):
        app = self._app(commands, ui_to_command_queue, command_to_ui_queue)
        app.MainLoop()
