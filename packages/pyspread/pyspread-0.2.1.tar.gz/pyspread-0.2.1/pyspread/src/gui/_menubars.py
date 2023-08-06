#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
_menubars
===========

Provides menubars

Provides:
---------
  1. ContextMenu: Context menu for main grid
  2. MainMenu: Main menu of pyspread

"""

import gettext

import wx

from _events import *

_ = gettext.gettext


class _filledMenu(wx.Menu):
    """Menu that fills from the attribute menudata.

    Parameters:
    parent: object
    \tThe parent object that hosts the event handler methods
    menubar: wx.Menubar, defaults to parent
    \tThe menubar to which the menu is attached

    menudata has the following structure:
    [
        [wx.Menu, _("Menuname"), [\
            [wx.MenuItem, ["Methodname"), _("Itemlabel"), _("Help")]] , \
            ...
            "Separator" , \
            ...
            [wx.Menu, ...], \
            ...
        ] , \
    ...
    ]

    """

    menudata = []

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent')
        try:
            self.menubar = kwargs.pop('menubar')
        except KeyError:
            self.menubar = self.parent
        wx.Menu.__init__(self, *args, **kwargs)

        # id - message type storage
        self.ids_msgs = {}

        # Stores approve_item for disabling
        self.approve_item = None

        self._add_submenu(self, self.menudata)

    def _add_submenu(self, parent, data):
        """Adds items in data as a submenu to parent"""

        for item in data:
            obj = item[0]
            if obj == wx.Menu:
                try:
                    _, menuname, submenu, menu_id = item
                except ValueError:
                    _, menuname, submenu = item
                    menu_id = -1

                menu = obj()
                self._add_submenu(menu, submenu)

                if parent == self:
                    self.menubar.Append(menu, menuname)
                else:
                    parent.AppendMenu(menu_id, menuname, menu)

            elif obj == wx.MenuItem:
                try:
                    msgtype, shortcut, helptext, item_id = item[1]
                except ValueError:
                    msgtype, shortcut, helptext = item[1]
                    item_id = wx.NewId()

                try:
                    style = item[2]
                except IndexError:
                    style = wx.ITEM_NORMAL

                menuitem = obj(parent, item_id, shortcut, helptext, style)

                parent.AppendItem(menuitem)

                if "&Approve file" == shortcut:
                    self.approve_item = menuitem

                self.ids_msgs[item_id] = msgtype

                self.parent.Bind(wx.EVT_MENU, self.OnMenu, id=item_id)

            elif obj == "Separator":
                parent.AppendSeparator()

            else:
                raise TypeError, _("Menu item unknown")

    def OnMenu(self, event):
        """Menu event handler"""

        msgtype = self.ids_msgs[event.GetId()]
        post_command_event(self.parent, msgtype)

# end of class _filledMenu


class ContextMenu(_filledMenu):
    """Context menu for grid operations"""

    item = wx.MenuItem
    menudata = [ \
    [item, [CutMsg, _("Cu&t\tCtrl+x"), _("Cut cell to clipboard")]], \
    [item, [CopyMsg, _("&Copy\tCtrl+c"),
            _("Copy input strings to clipboard")]], \
    [item, [PasteMsg, _("&Paste\tCtrl+v"), _("Paste cell from clipboard")]], \
    [item, [InsertRowsMsg, _("Insert &rows\tShift+Ctrl+i"),
            _("Insert rows at cursor")]], \
    [item, [InsertColsMsg, _("&Insert columns\tCtrl+i"),
            _("Insert columns at cursor")]], \
    [item, [DeleteRowsMsg, _("Delete rows\tShift+Ctrl+d"), _("Delete rows")]],
    [item, [DeleteColsMsg, _("Delete columns\tCtrl+Alt+d"),
            _("Delete columns")]],
    ]


# end of class ContextMenu


class MainMenu(_filledMenu):
    """Main application menu"""
    item = wx.MenuItem
    menudata = [ \
        [wx.Menu, _("&File"), [\
            [item, [NewMsg, _("&New\tCtrl+n"),
                _("Create a new, empty spreadsheet"), wx.ID_NEW]], \
            [item, [OpenMsg, _("&Open"),
                _("Open spreadsheet from file"), wx.ID_OPEN]], \
            ["Separator"], \
            [item, [SaveMsg, _("&Save\tCtrl+s"),
                    _("Save spreadsheet"), wx.ID_SAVE]], \
            [item, [SaveAsMsg, _("Save &As\tShift+Ctrl+s"),
                _("Save spreadsheet to a new file")], wx.ID_SAVEAS], \
            ["Separator"], \
            [item, [ImportMsg, _("&Import"),
                _("Import a file and paste it into current grid")]], \
            [item, [ExportMsg, _("&Export"),
                _("Export selection to file (Supported formats: CSV)")]], \
            ["Separator"], \
            [item, [ApproveMsg, _("&Approve file"),
                _("Approve, unfreeze and sign the current file")]], \
            ["Separator"], \
            [item, [PageSetupMsg, _("Page setup"),
                _("Setup printer page")]], \
            [item, [PrintPreviewMsg, _("Print preview\tShift+Ctrl+p"),
                _("Print preview"), wx.ID_PREVIEW]], \
            [item, [PrintMsg, _("&Print\tCtrl+p"),
                _("Print current spreadsheet"), wx.ID_PRINT]], \
            ["Separator"], \
            [item, [PreferencesMsg, _("Preferences..."),
                _("Change preferences of pyspread"), wx.ID_PREFERENCES]], \
            ["Separator"], \
            [item, [CloseMsg, _("&Quit\tCtrl+q"), _("Quit pyspread"),
                    wx.ID_EXIT]]] \
        ], \
        [wx.Menu, _("&Edit"), [\
            [item, [UndoMsg, _("&Undo\tCtrl+z"), _("Undo last step"),
                    wx.ID_UNDO]], \
            [item, [RedoMsg, _("&Redo\tShift+Ctrl+z"),
                _("Redo last undone step"), wx.ID_REDO]], \
            ["Separator"], \
            [item, [CutMsg, _("Cu&t\tCtrl+x"), _("Cut cell to clipboard")]], \
            [item, [CopyMsg, _("&Copy\tCtrl+c"),
                _("Copy the input strings of the cells to clipboard")]], \
            [item, [CopyResultMsg, _("Copy &Results\tShift+Ctrl+c"),
                _("Copy the result strings of the cells to the clipboard")]], \
            [item, [PasteMsg, _("&Paste\tCtrl+v"),
                _("Paste cells from clipboard"), wx.ID_PASTE]], \
            ["Separator"], \
            [item, [FindFocusMsg, _("&Find\tCtrl+f"),
                    _("Find cell by content")]], \
            [item, [ReplaceMsg, _("Replace...\tCtrl+Shift+f"),
                _("Replace strings in cells")]], \
            ["Separator"], \
            [item, [InsertRowsMsg, _("Insert &rows"),
                _("Insert rows at cursor")]], \
            [item, [InsertColsMsg, _("&Insert columns"),
                _("Insert columns at cursor")]], \
            [item, [InsertTabsMsg, _("Insert &table"),
                _("Insert table before current table")]], \
            ["Separator"], \
            [item, [DeleteRowsMsg, _("Delete rows"),
                _("Delete rows")]], \
            [item, [DeleteColsMsg, _("Delete columns"),
                _("Delete columns")]], \
            [item, [DeleteTabsMsg, _("Delete table"),
                _("Delete current table")]], \
            ["Separator"], \
            [item, [ShowResizeGridDialogMsg, _("Resize grid"),
                    _("Resize grid")]]] \
        ], \
        [wx.Menu, _("&View"), [ \
            [wx.Menu, _("Toolbars"), [ \
                [item, [MainToolbarToggleMsg, _("Main toolbar"),
                    _("Shows and hides the main toolbar.")], wx.ITEM_CHECK],
                [item, [AttributesToolbarToggleMsg, _("Format toolbar"),
                    _("Shows and hides the format toolbar.")], wx.ITEM_CHECK],
                [item, [FindToolbarToggleMsg, _("Find toolbar"),
                    _("Shows and hides the find toolbar.")], wx.ITEM_CHECK],
                ],
            ],
            [item, [EntryLineToggleMsg, _("Entry line"),
                    _("Shows and hides the entry line.")], wx.ITEM_CHECK],
            [item, [TableChoiceToggleMsg, _("Table choice"),
                    _("Shows and hides the table choice.")], wx.ITEM_CHECK],
            ["Separator"], \
            [item, [DisplayGotoCellDialogMsg, _("Go to cell\tCtrl+G"),
                        _("Moves the grid to a cell.")]],
            ["Separator"], \
            [item, [ZoomInMsg, _("Zoom in\tCtrl++"),
                        _("Zoom in grid.")]],
            [item, [ZoomOutMsg, _("Zoom out\tCtrl+-"),
                        _("Zoom out grid.")]],
            [item, [ZoomStandardMsg, _("Normal size\tCtrl+0"),
                        _("Show grid in standard zoom.")]],
            ["Separator"], \
            [item, [RefreshSelectionMsg, _("Refresh selected cells\tF5"),
                        _("Refresh selected cells even when frozen")]],
            ], \
        ], \
        [wx.Menu, _("F&ormat"), [ \
            [item, [FontDialogMsg, _("Font..."),
                        _("Launch font dialog.")]],
            [item, [FontUnderlineMsg, _("Underline"),
                        _("Toggles underline."), wx.ID_UNDERLINE]],
            [item, [FontStrikethroughMsg, _("Strikethrough"),
                        _("Toggles strikethrough.")]],
            ["Separator"], \
            [item, [FrozenMsg, _("Frozen"),
                     _("Toggles frozen state of cell. ") + \
                     _("Frozen cells are updated only when F5 is pressed.")]],
            ["Separator"], \
            [wx.Menu, _("Justification"), [ \
                [item, [JustificationMsg, justification, justification] \
                ] for justification in [_("Left"), _("Center"), _("Right")]]
                ], \
            [wx.Menu, _("Alignment"), [ \
                [item, [AlignmentMsg, alignment, alignment] \
                ] for alignment in [_("Top"), _("Center"), _("Bottom")]]
                ], \
            ["Separator"], \
            [item, [TextColorDialogMsg, _("Text color..."),
                    _("Launch color dialog to specify text color.")]],
            [item, [BgColorDialogMsg, _("Background color..."),
                    _("Launch color dialog to specify background color.")]],
            ["Separator"], \
            [item, [RotationDialogMsg, _("Rotation..."),
                    _("Set text rotation.")]
                ]
            ],
        ], \
        [wx.Menu, _("&Macro"), [\
            [item, [MacroListMsg, _("&Macro list\tCtrl+m"),
                        _("Choose, fill in, manage, and create macros")]], \
            [item, [MacroLoadMsg, _("&Load macro list"),
                        _("Load macro list")]], \
            [item, [MacroSaveMsg, _("&Save macro list"),
                        _("Save macro list")]]]], \
        [wx.Menu, _("&Help"), [\
            [item, [ManualMsg, _("First &Steps"),
                _("Launch First Steps in pyspread")]],
            [item, [TutorialMsg, _("&Tutorial"), _("Launch tutorial")]],
            [item, [FaqMsg, _("&FAQ"), _("Frequently asked questions")]],
            ["Separator"], \
            [item, [PythonTutorialMsg, _("&Python tutorial"),
                _("Python tutorial for coding information (online)")]],
            ["Separator"], \
            [item, [AboutMsg, _("&About"), _("About pyspread"), wx.ID_ABOUT]],
            ] \
        ] \
    ]

    def enable_file_approve(self, enable=True):
        """Enables or disables menu item (for entering/leaving save mode)"""

        self.approve_item.Enable(enable)

# end of class MainMenu