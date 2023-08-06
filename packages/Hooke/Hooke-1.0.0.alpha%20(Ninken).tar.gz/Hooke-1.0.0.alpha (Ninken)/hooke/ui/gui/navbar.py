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

"""Navigation bar for Hooke.
"""

import wx
#import wx.aui as aui         # C++ implementation
import wx.lib.agw.aui as aui  # Python implementation

from ...util.callback import callback, in_callback


class NavBar (aui.AuiToolBar):
    def __init__(self, callbacks, *args, **kwargs):
        super(NavBar, self).__init__(*args, **kwargs)
        bitmap_size = wx.Size(16,16)
        self.SetToolBitmapSize(bitmap_size)
        self._c = {
            'previous': self.AddTool(
                tool_id=wx.ID_PREVIEW_PREVIOUS,
                label='Previous',
                bitmap=wx.ArtProvider_GetBitmap(
                    wx.ART_GO_BACK, wx.ART_OTHER, bitmap_size),
                disabled_bitmap=wx.NullBitmap,
                kind=wx.ITEM_NORMAL,
                short_help_string='Previous curve',
                long_help_string='',
                client_data=None),
            'next': self.AddTool(
                tool_id=wx.ID_PREVIEW_NEXT,
                label='Next',
                bitmap=wx.ArtProvider_GetBitmap(
                    wx.ART_GO_FORWARD, wx.ART_OTHER, bitmap_size),
                disabled_bitmap=wx.NullBitmap,
                kind=wx.ITEM_NORMAL,
                short_help_string='Next curve',
                long_help_string='',
                client_data=None),
            'delete': self.AddTool(
                tool_id=wx.ID_DELETE,
                label='Delete',
                bitmap=wx.ArtProvider_GetBitmap(
                    wx.ART_DELETE, wx.ART_OTHER, bitmap_size),
                disabled_bitmap=wx.NullBitmap,
                kind=wx.ITEM_NORMAL,
                short_help_string='Remove curve from playlist',
                long_help_string='',
                client_data=None),
            }
        self.Realize()
        self._callbacks = callbacks
        self.Bind(wx.EVT_TOOL, self._on_next, self._c['next'])
        self.Bind(wx.EVT_TOOL, self._on_previous, self._c['previous'])
        self.Bind(wx.EVT_TOOL, self._on_delete, self._c['delete'])

    def _on_next(self, event):
        self.next()

    def _on_previous(self, event):
        self.previous()

    def _on_delete(self, event):
        self.delete()

    @callback
    def next(self):
        pass

    @callback
    def previous(self):
        pass

    @callback
    def delete(self):
        pass
