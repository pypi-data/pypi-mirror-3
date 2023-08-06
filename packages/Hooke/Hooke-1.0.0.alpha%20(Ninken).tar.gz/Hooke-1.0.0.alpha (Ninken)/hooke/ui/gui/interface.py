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

"""Define :class:`HookeApp` and related, central application classes.
"""

WX_GOOD=['2.9']

import wxversion
wxversion.select(WX_GOOD)

import copy
import logging
import os
import os.path
import platform
import shutil
import time

import wx
import wx.html
#import wx.aui as aui         # C++ implementation
import wx.lib.agw.aui as aui  # Python implementation
import wx.lib.evtmgr as evtmgr
# wxPropertyGrid is included in wxPython >= 2.9.1, see
#   http://wxpropgrid.sourceforge.net/cgi-bin/index?page=download
# until then, we'll avoid it because of the *nix build problems.
#import wx.propgrid as wxpg

from ...command import CommandExit, Exit, Success, Failure, Command, Argument
from ...engine import CommandMessage
from ...interaction import Request, BooleanRequest, ReloadUserInterfaceConfig
from .dialog.selection import Selection as SelectionDialog
from .dialog.save_file import select_save_file
from . import menu as menu
from . import navbar as navbar
from . import panel as panel
from .panel.propertyeditor import props_from_argument, props_from_setting
from . import statusbar as statusbar


class HookeFrame (wx.Frame):
    """The main Hooke-interface window.    
    """
    def __init__(self, gui, commands, inqueue, outqueue, *args, **kwargs):
        super(HookeFrame, self).__init__(*args, **kwargs)
        self.log = logging.getLogger('hooke')
        self.gui = gui
        self.commands = commands
        self.inqueue = inqueue
        self.outqueue = outqueue
        self._perspectives = {}  # {name: perspective_str}
        self._c = {}

        self.SetIcon(wx.Icon(
                os.path.expanduser(self.gui.config['icon image']),
                wx.BITMAP_TYPE_ICO))

        # setup frame manager
        self._c['manager'] = aui.AuiManager()
        self._c['manager'].SetManagedWindow(self)

        # set the gradient and drag styles
        self._c['manager'].GetArtProvider().SetMetric(
            aui.AUI_DOCKART_GRADIENT_TYPE, aui.AUI_GRADIENT_NONE)

        # Min size for the frame itself isn't completely done.  See
        # the end of FrameManager::Update() for the test code. For
        # now, just hard code a frame minimum size.
        #self.SetMinSize(wx.Size(500, 500))

        self._setup_panels()
        self._setup_toolbars()
        self._c['manager'].Update()  # commit pending changes

        # Create the menubar after the panes so that the default
        # perspective is created with all panes open
        panels = [p for p in self._c.values() if isinstance(p, panel.Panel)]
        self._c['menu bar'] = menu.HookeMenuBar(
            parent=self,
            panels=panels,
            callbacks={
                'close': self._on_close,
                'about': self._on_about,
                'view_panel': self._on_panel_visibility,
                'save_perspective': self._on_save_perspective,
                'delete_perspective': self._on_delete_perspective,
                'select_perspective': self._on_select_perspective,
                })
        self.SetMenuBar(self._c['menu bar'])

        self._c['status bar'] = statusbar.StatusBar(
            parent=self,
            style=wx.ST_SIZEGRIP)
        self.SetStatusBar(self._c['status bar'])

        self._setup_perspectives()
        self._bind_events()
        return # TODO: cleanup
        self._displayed_plot = None
        #load default list, if possible
        self.do_loadlist(self.GetStringFromConfig('core', 'preferences', 'playlists'))


    # GUI maintenance

    def _setup_panels(self):
        client_size = self.GetClientSize()
        for p,style in [
#            ('folders', wx.GenericDirCtrl(
#                    parent=self,
#                    dir=self.gui.config['folders-workdir'],
#                    size=(200, 250),
#                    style=wx.DIRCTRL_SHOW_FILTERS,
#                    filter=self.gui.config['folders-filters'],
#                    defaultFilter=self.gui.config['folders-filter-index']), 'left'),
            (panel.PANELS['playlist'](
                    callbacks={
                        '_delete_playlist':self._delete_playlist,
                        '_delete_curve':self._delete_curve,
                        '_on_set_selected_playlist':self._on_set_selected_playlist,
                        '_on_set_selected_curve':self._on_set_selected_curve,
                        },
                    parent=self,
                    style=wx.WANTS_CHARS|wx.NO_BORDER,
                    # WANTS_CHARS so the panel doesn't eat the Return key.
#                    size=(160, 200),
                    ), 'left'),
            (panel.PANELS['note'](
                    callbacks = {
                        '_on_update':self._on_update_note,
                        },
                    parent=self,
                    style=wx.WANTS_CHARS|wx.NO_BORDER,
#                    size=(160, 200),
                    ), 'left'),
#            ('notebook', Notebook(
#                    parent=self,
#                    pos=wx.Point(client_size.x, client_size.y),
#                    size=wx.Size(430, 200),
#                    style=aui.AUI_NB_DEFAULT_STYLE
#                    | aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER), 'center'),
            (panel.PANELS['commands'](
                    commands=self.commands,
                    selected=self.gui.config['selected command'],
                    callbacks={
                        'execute': self.explicit_execute_command,
                        'select_plugin': self.select_plugin,
                        'select_command': self.select_command,
#                        'selection_changed': self.panelProperties.select(self, method, command),  #SelectedTreeItem = selected_item,
                        },
                    parent=self,
                    style=wx.WANTS_CHARS|wx.NO_BORDER,
                    # WANTS_CHARS so the panel doesn't eat the Return key.
#                    size=(160, 200),
                    ), 'right'),
            (panel.PANELS['propertyeditor'](
                    callbacks={},
                    parent=self,
                    style=wx.WANTS_CHARS,
                    # WANTS_CHARS so the panel doesn't eat the Return key.
                    ), 'center'),
            (panel.PANELS['plot'](
                    callbacks={
                        '_set_status_text': self._on_plot_status_text,
                        },
                    parent=self,
                    style=wx.WANTS_CHARS|wx.NO_BORDER,
                    # WANTS_CHARS so the panel doesn't eat the Return key.
#                    size=(160, 200),
                    ), 'center'),
            (panel.PANELS['output'](
                    parent=self,
                    pos=wx.Point(0, 0),
                    size=wx.Size(150, 90),
                    style=wx.TE_READONLY|wx.NO_BORDER|wx.TE_MULTILINE),
             'bottom'),
            ]:
            self._add_panel(p, style)
        self.execute_command(  # setup already loaded playlists
            command=self._command_by_name('playlists'))
        self.execute_command(  # setup already loaded curve
            command=self._command_by_name('get curve'))

    def _add_panel(self, panel, style):
        self._c[panel.name] = panel
        m_name = panel.managed_name
        info = aui.AuiPaneInfo().Name(m_name).Caption(m_name)
        info.PaneBorder(False).CloseButton(True).MaximizeButton(False)
        if style == 'top':
            info.Top()
        elif style == 'center':
            info.CenterPane()
        elif style == 'left':
            info.Left()
        elif style == 'right':
            info.Right()
        else:
            assert style == 'bottom', style
            info.Bottom()
        self._c['manager'].AddPane(panel, info)

    def _setup_toolbars(self):
        self._c['navigation bar'] = navbar.NavBar(
            callbacks={
                'next': self._next_curve,
                'previous': self._previous_curve,
                'delete': self._delete_curve,
                },
            parent=self)
        self._c['manager'].AddPane(
            self._c['navigation bar'],
            aui.AuiPaneInfo().Name('Navigation').Caption('Navigation'
                ).ToolbarPane().Top().Layer(1).Row(1).LeftDockable(False
                ).RightDockable(False))

    def _bind_events(self):
        # TODO: figure out if we can use the eventManager for menu
        # ranges and events of 'self' without raising an assertion
        # fail error.
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self._on_pane_close)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)

        return # TODO: cleanup
        treeCtrl = self._c['folders'].GetTreeCtrl()
        treeCtrl.Bind(wx.EVT_LEFT_DCLICK, self._on_dir_ctrl_left_double_click)

    def _on_about(self, *args):
        dialog = wx.MessageDialog(
            parent=self,
            message=self.gui._splash_text(extra_info={
                    'get-details':'click "Help -> License"'},
                                          wrap=False),
            caption='About Hooke',
            style=wx.OK|wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()

    def _on_size(self, event):
        event.Skip()

    def _on_close(self, *args):
        self.log.info('closing GUI framework')

        # apply changes
        self._set_config('main height', self.GetSize().GetHeight())
        self._set_config('main left', self.GetPosition()[0])
        self._set_config('main top', self.GetPosition()[1])
        self._set_config('main width', self.GetSize().GetWidth())
        self._c['manager'].UnInit()
        del self._c['manager']
        self.Destroy()

    def _on_erase_background(self, event):
        event.Skip()

    def _on_key(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_RIGHT:
            self._next_curve()
        elif code == wx.WXK_LEFT:
            self._previous_curve()
        elif code == wx.WXK_DELETE or code == wx.WXK_BACK:
            self._delete_curve()
        else:
            event.Skip()


    # Panel utility functions

    def _file_name(self, name):
        """Cleanup names according to configured preferences.
        """
        if self.gui.config['hide extensions'] == True:
            name,ext = os.path.splitext(name)
        return name



    # Command handling

    def _command_by_name(self, name):
        cs = [c for c in self.commands if c.name == name]
        if len(cs) == 0:
            raise KeyError(name)
        elif len(cs) > 1:
            raise Exception('Multiple commands named "%s"' % name)
        return cs[0]

    def explicit_execute_command(self, _class=None, method=None,
                                 command=None, args=None):
        return self.execute_command(
            _class=_class, method=method, command=command, args=args,
            explicit_user_call=True)

    def execute_command(self, _class=None, method=None,
                        command=None, args=None, explicit_user_call=False):
        if args == None:
            args = {}
        if ('property editor' in self._c
            and self.gui.config['selected command'] == command.name):
            for name,value in self._c['property editor'].get_values().items():
                arg = self._c['property editor']._argument_from_label.get(
                    name, None)
                if arg == None:
                    continue
                elif arg.count == 1:
                    args[arg.name] = value
                    continue
                # deal with counted arguments
                if arg.name not in args:
                    args[arg.name] = {}
                index = int(name[len(arg.name):])
                args[arg.name][index] = value
            for arg in command.arguments:
                if arg.name not in args:
                    continue  # undisplayed argument, e.g. 'driver' types.
                count = arg.count
                if hasattr(arg, '_display_count'):  # support HACK in props_from_argument()
                    count = arg._display_count
                if count != 1 and arg.name in args:
                    keys = sorted(args[arg.name].keys())
                    assert keys == range(count), keys
                    args[arg.name] = [args[arg.name][i]
                                      for i in range(count)]
                if arg.count == -1:
                    while (len(args[arg.name]) > 0
                           and args[arg.name][-1] == None):
                        args[arg.name].pop()
                    if len(args[arg.name]) == 0:
                        args[arg.name] = arg.default
        cm = CommandMessage(command.name, args)
        self.gui._submit_command(
            cm, self.inqueue, explicit_user_call=explicit_user_call)
        # TODO: skip responses for commands that were captured by the
        # command stack.  We'd need to poll on each request, remember
        # capture state, or add a flag to the response...
        return self._handle_response(command_message=cm)

    def _handle_response(self, command_message):
        results = []
        while True:
            msg = self.outqueue.get()
            results.append(msg)
            if isinstance(msg, Exit):
                self._on_close()
                break
            elif isinstance(msg, CommandExit):
                # TODO: display command complete
                break
            elif isinstance(msg, ReloadUserInterfaceConfig):
                self.gui.reload_config(msg.config)
                continue
            elif isinstance(msg, Request):
                h = handler.HANDLERS[msg.type]
                h.run(self, msg)  # TODO: pause for response?
                continue
        pp = getattr(
           self, '_postprocess_%s' % command_message.command.replace(' ', '_'),
           self._postprocess_text)
        pp(command=command_message.command,
           args=command_message.arguments,
           results=results)
        return results

    def _handle_request(self, msg):
        """Repeatedly try to get a response to `msg`.
        """
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
                        error.__class__.__name__, ': ', str(error), '\n']))
            self.cmd.stdout.write(prompt_string)
            value = parser(msg, self.cmd.stdin.readline())
            try:
                response = msg.response(value)
                break
            except ValueError, error:
                continue
        self.inqueue.put(response)

    def _set_config(self, option, value, section=None):
        self.gui._set_config(section=section, option=option, value=value,
                             ui_to_command_queue=self.inqueue,
                             response_handler=self._handle_response)


    # Command-specific postprocessing

    def _postprocess_text(self, command, args={}, results=[]):
        """Print the string representation of the results to the Results window.

        This is similar to :class:`~hooke.ui.commandline.DoCommand`'s
        approach, except that :class:`~hooke.ui.commandline.DoCommand`
        doesn't print some internally handled messages
        (e.g. :class:`~hooke.interaction.ReloadUserInterfaceConfig`).
        """
        for result in results:
            if isinstance(result, CommandExit):
                self._c['output'].write(result.__class__.__name__+'\n')
            self._c['output'].write(str(result).rstrip()+'\n')

    def _postprocess_playlists(self, command, args={}, results=None):
        """Update `self` to show the playlists.
        """
        if not isinstance(results[-1], Success):
            self._postprocess_text(command, results=results)
            return
        assert len(results) == 2, results
        playlists = results[0]
        if 'playlist' in self._c:
            for playlist in playlists:
                if self._c['playlist'].is_playlist_loaded(playlist):
                    self._c['playlist'].update_playlist(playlist)
                else:
                    self._c['playlist'].add_playlist(playlist)

    def _postprocess_new_playlist(self, command, args={}, results=None):
        """Update `self` to show the new playlist.
        """
        if not isinstance(results[-1], Success):
            self._postprocess_text(command, results=results)
            return
        assert len(results) == 2, results
        playlist = results[0]
        if 'playlist' in self._c:
            loaded = self._c['playlist'].is_playlist_loaded(playlist)
            assert loaded == False, loaded
            self._c['playlist'].add_playlist(playlist)

    def _postprocess_load_playlist(self, command, args={}, results=None):
        """Update `self` to show the playlist.
        """
        if not isinstance(results[-1], Success):
            self._postprocess_text(command, results=results)
            return
        assert len(results) == 2, results
        playlist = results[0]
        self._c['playlist'].add_playlist(playlist)

    def _postprocess_get_playlist(self, command, args={}, results=[]):
        if not isinstance(results[-1], Success):
            self._postprocess_text(command, results=results)
            return
        assert len(results) == 2, results
        playlist = results[0]
        if 'playlist' in self._c:
            loaded = self._c['playlist'].is_playlist_loaded(playlist)
            assert loaded == True, loaded
            self._c['playlist'].update_playlist(playlist)

    def _postprocess_name_playlist(self, command, args={}, results=None):
        """Update `self` to show the new playlist.
        """
        return self._postprocess_new_playlist(command, args, results)

    def _postprocess_get_curve(self, command, args={}, results=[]):
        """Update `self` to show the curve.
        """
        if not isinstance(results[-1], Success):
            self._postprocess_text(command, results=results)
            return
        assert len(results) == 2, results
        curve = results[0]
        if args.get('curve', None) == None:
            # the command defaults to the current curve of the current playlist
            results = self.execute_command(
                command=self._command_by_name('get playlist'))
            playlist = results[0]
        else:
            raise NotImplementedError()
        if 'note' in self._c:
            self._c['note'].set_text(curve.info.get('note', ''))
        if 'playlist' in self._c:
            self._c['playlist'].set_selected_curve(
                playlist, curve)
        if 'plot' in self._c:
            self._c['plot'].set_curve(curve, config=self.gui.config)

    def _postprocess_next_curve(self, command, args={}, results=[]):
        """No-op.  Only call 'next curve' via `self._next_curve()`.
        """
        pass

    def _postprocess_previous_curve(self, command, args={}, results=[]):
        """No-op.  Only call 'previous curve' via `self._previous_curve()`.
        """
        pass

    def _postprocess_glob_curves_to_playlist(
        self, command, args={}, results=[]):
        """Update `self` to show new curves.
        """
        if not isinstance(results[-1], Success):
            self._postprocess_text(command, results=results)
            return
        if 'playlist' in self._c:
            if args.get('playlist', None) != None:
                playlist = args['playlist']
                pname = playlist.name
                loaded = self._c['playlist'].is_playlist_name_loaded(pname)
                assert loaded == True, loaded
                for curve in results[:-1]:
                    self._c['playlist']._add_curve(pname, curve)
            else:
                self.execute_command(
                    command=self._command_by_name('get playlist'))

    def _postprocess_delete_curve(self, command, args={}, results=[]):
        """No-op.  Only call 'delete curve' via `self._delete_curve()`.
        """
        pass

    def _update_curve(self, command, args={}, results=[]):
        """Update the curve, since the available columns may have changed.
        """
        if isinstance(results[-1], Success):
            self.execute_command(
                command=self._command_by_name('get curve'))


    # Command panel interface

    def select_command(self, _class, method, command):
        #self.select_plugin(plugin=command.plugin)
        self._c['property editor'].clear()
        self._c['property editor']._argument_from_label = {}
        for argument in command.arguments:
            if argument.name == 'help':
                continue

            results = self.execute_command(
                command=self._command_by_name('playlists'))
            if not isinstance(results[-1], Success):
                self._postprocess_text(command, results=results)
                playlists = []
            else:
                playlists = results[0]

            results = self.execute_command(
                command=self._command_by_name('playlist curves'))
            if not isinstance(results[-1], Success):
                self._postprocess_text(command, results=results)
                curves = []
            else:
                curves = results[0]

            ret = props_from_argument(
                argument, curves=curves, playlists=playlists)
            if ret == None:
                continue  # property intentionally not handled (yet)
            for label,p in ret:
                self._c['property editor'].append_property(p)
                self._c['property editor']._argument_from_label[label] = (
                    argument)

        self._set_config('selected command', command.name)

    def select_plugin(self, _class=None, method=None, plugin=None):
        pass



    # Folders panel interface

    def _on_dir_ctrl_left_double_click(self, event):
        file_path = self.panelFolders.GetPath()
        if os.path.isfile(file_path):
            if file_path.endswith('.hkp'):
                self.do_loadlist(file_path)
        event.Skip()



    # Note panel interface

    def _on_update_note(self, _class, method, text):
        """Sets the note for the active curve.
        """
        self.execute_command(
            command=self._command_by_name('set note'),
            args={'note':text})



    # Playlist panel interface

    def _delete_playlist(self, _class, method, playlist):
        #if hasattr(playlist, 'path') and playlist.path != None:
        #    os.remove(playlist.path)
        # TODO: remove playlist from underlying hooke instance and call ._c['playlist'].delete_playlist()
        # possibly rename this method to _postprocess_delete_playlist...
        pass

    def _on_set_selected_playlist(self, _class, method, playlist):
        """Call the `jump to playlist` command.
        """
        results = self.execute_command(
            command=self._command_by_name('playlists'))
        if not isinstance(results[-1], Success):
            return
        assert len(results) == 2, results
        playlists = results[0]
        matching = [p for p in playlists if p.name == playlist.name]
        assert len(matching) == 1, matching
        index = playlists.index(matching[0])
        results = self.execute_command(
            command=self._command_by_name('jump to playlist'),
            args={'index':index})

    def _on_set_selected_curve(self, _class, method, playlist, curve):
        """Call the `jump to curve` command.
        """
        self._on_set_selected_playlist(_class, method, playlist)
        index = playlist.index(curve)
        results = self.execute_command(
            command=self._command_by_name('jump to curve'),
            args={'index':index})
        if not isinstance(results[-1], Success):
            return
        #results = self.execute_command(
        #    command=self._command_by_name('get playlist'))
        #if not isinstance(results[-1], Success):
        #    return
        self.execute_command(
            command=self._command_by_name('get curve'))



    # Plot panel interface

    def _on_plot_status_text(self, _class, method, text):
        if 'status bar' in self._c:
            self._c['status bar'].set_plot_text(text)



    # Navbar interface

    def _next_curve(self, *args):
        """Call the `next curve` command.
        """
        results = self.execute_command(
            command=self._command_by_name('next curve'))
        if isinstance(results[-1], Success):
            self.execute_command(
                command=self._command_by_name('get curve'))

    def _previous_curve(self, *args):
        """Call the `previous curve` command.
        """
        results = self.execute_command(
            command=self._command_by_name('previous curve'))
        if isinstance(results[-1], Success):
            self.execute_command(
                command=self._command_by_name('get curve'))

    def _delete_curve(self, *args, **kwargs):
        cmd_kwargs = {}
        playlist = kwargs.get('playlist', None)
        curve = kwargs.get('curve', None)
        if playlist is not None and curve is not None:
            cmd_kwargs['index'] = playlist.index(curve)
        results = self.execute_command(
            command=self._command_by_name('remove curve from playlist'),
            args=cmd_kwargs)
        if isinstance(results[-1], Success):
            results = self.execute_command(
                command=self._command_by_name('get playlist'))


    # Panel display handling

    def _on_pane_close(self, event):
        pane = event.pane
        view = self._c['menu bar']._c['view']
        if pane.name in  view._c.keys():
            view._c[pane.name].Check(False)
        event.Skip()

    def _on_panel_visibility(self, _class, method, panel_name, visible):
        pane = self._c['manager'].GetPane(panel_name)
        pane.Show(visible)
        #if we don't do the following, the Folders pane does not resize properly on hide/show
        if pane.caption == 'Folders' and pane.IsShown() and pane.IsDocked():
            #folders_size = pane.GetSize()
            self.panelFolders.Fit()
        self._c['manager'].Update()

    def _setup_perspectives(self):
        """Add perspectives to menubar and _perspectives.
        """
        self._perspectives = {
            'Default': self._c['manager'].SavePerspective(),
            }
        path = os.path.expanduser(self.gui.config['perspective path'])
        if os.path.isdir(path):
            files = sorted(os.listdir(path))
            for fname in files:
                name, extension = os.path.splitext(fname)
                if extension != self.gui.config['perspective extension']:
                    continue
                fpath = os.path.join(path, fname)
                if not os.path.isfile(fpath):
                    continue
                perspective = None
                with open(fpath, 'rU') as f:
                    perspective = f.readline()
                if perspective:
                    self._perspectives[name] = perspective

        selected_perspective = self.gui.config['active perspective']
        if not self._perspectives.has_key(selected_perspective):
            self._set_config('active perspective', 'Default')

        self._restore_perspective(selected_perspective, force=True)
        self._update_perspective_menu()

    def _update_perspective_menu(self):
        self._c['menu bar']._c['perspective'].update(
            sorted(self._perspectives.keys()),
            self.gui.config['active perspective'])

    def _save_perspective(self, perspective, perspective_dir, name,
                          extension=None):
        path = os.path.join(perspective_dir, name)
        if extension != None:
            path += extension
        if not os.path.isdir(perspective_dir):
            os.makedirs(perspective_dir)
        with open(path, 'w') as f:
            f.write(perspective)
        self._perspectives[name] = perspective
        self._restore_perspective(name)
        self._update_perspective_menu()

    def _delete_perspectives(self, perspective_dir, names,
                             extension=None):
        self.log.debug('remove perspectives %s from %s'
                       % (names, perspective_dir))
        for name in names:
            path = os.path.join(perspective_dir, name)
            if extension != None:
                path += extension
            os.remove(path)
            del(self._perspectives[name])
        self._update_perspective_menu()
        if self.gui.config['active perspective'] in names:
            self._restore_perspective('Default')
        # TODO: does this bug still apply?
        # Unfortunately, there is a bug in wxWidgets for win32 (Ticket #3258
        #   http://trac.wxwidgets.org/ticket/3258 
        # ) that makes the radio item indicator in the menu disappear.
        # The code should be fine once this issue is fixed.

    def _restore_perspective(self, name, force=False):
        if name != self.gui.config['active perspective'] or force == True:
            self.log.debug('restore perspective %s' % name)
            self._set_config('active perspective', name)
            self._c['manager'].LoadPerspective(self._perspectives[name])
            self._c['manager'].Update()
            for pane in self._c['manager'].GetAllPanes():
                view = self._c['menu bar']._c['view']
                if pane.name in view._c.keys():
                    view._c[pane.name].Check(pane.window.IsShown())

    def _on_save_perspective(self, *args):
        perspective = self._c['manager'].SavePerspective()
        name = self.gui.config['active perspective']
        if name == 'Default':
            name = 'New perspective'
        name = select_save_file(
            directory=os.path.expanduser(self.gui.config['perspective path']),
            name=name,
            extension=self.gui.config['perspective extension'],
            parent=self,
            message='Enter a name for the new perspective:',
            caption='Save perspective')
        if name == None:
            return
        self._save_perspective(
            perspective,
            os.path.expanduser(self.gui.config['perspective path']), name=name,
            extension=self.gui.config['perspective extension'])

    def _on_delete_perspective(self, *args, **kwargs):
        options = sorted([p for p in self._perspectives.keys()
                          if p != 'Default'])
        dialog = SelectionDialog(
            options=options,
            message="\nPlease check the perspectives\n\nyou want to delete and click 'Delete'.\n",
            button_id=wx.ID_DELETE,
            selection_style='multiple',
            parent=self,
            title='Delete perspective(s)',
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        dialog.CenterOnScreen()
        dialog.ShowModal()
        if dialog.canceled == True:
            return
        names = [options[i] for i in dialog.selected]
        dialog.Destroy()
        self._delete_perspectives(
            os.path.expanduser(self.gui.config['perspective path']),
            names=names, extension=self.gui.config['perspective extension'])

    def _on_select_perspective(self, _class, method, name):
        self._restore_perspective(name)


# setup per-command versions of HookeFrame._update_curve
for _command in ['convert_distance_to_force',
                 'polymer_fit_peaks',
                 'remove_cantilever_from_extension',
                 'zero_surface_contact_point',
                 ]:
    setattr(HookeFrame, '_postprocess_%s' % _command, HookeFrame._update_curve)
del _command


class HookeApp (wx.App):
    """A :class:`wx.App` wrapper around :class:`HookeFrame`.

    Tosses up a splash screen and then loads :class:`HookeFrame` in
    its own window.
    """
    def __init__(self, gui, commands, inqueue, outqueue, *args, **kwargs):
        self.gui = gui
        self.commands = commands
        self.inqueue = inqueue
        self.outqueue = outqueue
        super(HookeApp, self).__init__(*args, **kwargs)

    def OnInit(self):
        self.SetAppName('Hooke')
        self.SetVendorName('')
        self._setup_splash_screen()

        height = self.gui.config['main height']
        width = self.gui.config['main width']
        top = self.gui.config['main top']
        left = self.gui.config['main left']

        # Sometimes, the ini file gets confused and sets 'left' and
        # 'top' to large negative numbers.  Here we catch and fix
        # this.  Keep small negative numbers, the user might want
        # those.
        if left < -width:
            left = 0
        if top < -height:
            top = 0

        self._c = {
            'frame': HookeFrame(
                self.gui, self.commands, self.inqueue, self.outqueue,
                parent=None, title='Hooke',
                pos=(left, top), size=(width, height),
                style=wx.DEFAULT_FRAME_STYLE|wx.SUNKEN_BORDER|wx.CLIP_CHILDREN),
            }
        self._c['frame'].Show(True)
        self.SetTopWindow(self._c['frame'])
        return True

    def _setup_splash_screen(self):
        if self.gui.config['show splash screen'] == True:
            path = os.path.expanduser(self.gui.config['splash screen image'])
            if os.path.isfile(path):
                duration = self.gui.config['splash screen duration']
                wx.SplashScreen(
                    bitmap=wx.Image(path).ConvertToBitmap(),
                    splashStyle=wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT,
                    milliseconds=duration,
                    parent=None)
                wx.Yield()
                # For some reason splashDuration and sleep do not
                # correspond to each other at least not on Windows.
                # Maybe it's because duration is in milliseconds and
                # sleep in seconds.  Thus we need to increase the
                # sleep time a bit. A factor of 1.2 seems to work.
                sleepFactor = 1.2
                time.sleep(sleepFactor * duration / 1000)
