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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread. If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
_events
=======

Event handler module

Provides
--------

* post_command_event: Posts a command event

"""

import wx
import wx.lib
import wx.lib.newevent

def post_command_event(target, msg_cls, **kwargs):
    """Posts command event to main window
    
    Command events propagate.
    
    Parameters
    ----------
     * msg_cls: class
    \tMessage class from new_command_event()
     * kwargs: dict
    \tMessage arguments
    
    """
    
    msg = msg_cls(id=-1, **kwargs)
    wx.PostEvent(target, msg)


new_command_event = wx.lib.newevent.NewCommandEvent
    
# Main window
# ===========

TitleMsg, EVT_COMMAND_TITLE = new_command_event()

SafeModeEntryMsg, EVT_COMMAND_SAFE_MODE_ENTRY = new_command_event()
SafeModeExitMsg, EVT_COMMAND_SAFE_MODE_EXIT = new_command_event()

CloseMsg, EVT_COMMAND_CLOSE = new_command_event()

ManualMsg, EVT_COMMAND_MANUAL = new_command_event()
TutorialMsg, EVT_COMMAND_TUTORIAL = new_command_event()
FaqMsg, EVT_COMMAND_FAQ = new_command_event()
PythonTutorialMsg, EVT_COMMAND_PYTHON_TURORIAL = new_command_event()
AboutMsg, EVT_COMMAND_ABOUT = new_command_event()

MacroListMsg, EVT_COMMAND_MACROLIST = new_command_event()
MacroReplaceMsg, EVT_COMMAND_MACROREPLACE = new_command_event()
MacroExecuteMsg, EVT_COMMAND_MACROEXECUTE = new_command_event()
MacroLoadMsg, EVT_COMMAND_MACROLOAD = new_command_event()
MacroSaveMsg, EVT_COMMAND_MACROSAVE = new_command_event()

MainToolbarToggleMsg, EVT_COMMAND_MAINTOOLBAR_TOGGLE = new_command_event()
AttributesToolbarToggleMsg, EVT_COMMAND_ATTRIBUTESTOOLBAR_TOGGLE = \
                                        new_command_event()
FindToolbarToggleMsg, EVT_COMMAND_FIND_TOOLBAR_TOGGLE = new_command_event()
EntryLineToggleMsg, EVT_COMMAND_ENTRYLINE_TOGGLE = new_command_event()
TableChoiceToggleMsg, EVT_COMMAND_TABLECHOICE_TOGGLE = new_command_event()

ToolbarUpdateMsg, EVT_COMMAND_TOOLBAR_UPDATE = new_command_event()

ContentChangedMsg, EVT_CONTENT_CHANGED = new_command_event()

# Grid cell
# =========

# Cell code entry events

CodeEntryMsg, EVT_COMMAND_CODE_ENTRY = new_command_event()

# Cell attribute events

FontDialogMsg, EVT_COMMAND_FONTDIALOG = new_command_event()
FontMsg, EVT_COMMAND_FONT = new_command_event()
FontSizeMsg, EVT_COMMAND_FONTSIZE = new_command_event()
FontBoldMsg, EVT_COMMAND_FONTBOLD = new_command_event()
FontItalicsMsg, EVT_COMMAND_FONTITALICS = new_command_event()
FontUnderlineMsg, EVT_COMMAND_FONTUNDERLINE = new_command_event()
FontStrikethroughMsg, EVT_COMMAND_FONTSTRIKETHROUGH = new_command_event()
FrozenMsg, EVT_COMMAND_FROZEN = new_command_event()
JustificationMsg, EVT_COMMAND_JUSTIFICATION = new_command_event()
AlignmentMsg, EVT_COMMAND_ALIGNMENT = new_command_event()
BorderChoiceMsg, EVT_COMMAND_BORDERCHOICE = new_command_event()
BorderWidthMsg, EVT_COMMAND_BORDERWIDTH = new_command_event()
BorderColorMsg, EVT_COMMAND_BORDERCOLOR = new_command_event()
BackgroundColorMsg, EVT_COMMAND_BACKGROUNDCOLOR = new_command_event()
TextColorMsg, EVT_COMMAND_TEXTCOLOR = new_command_event()
RotationDialogMsg,  EVT_COMMAND_ROTATIONDIALOG = new_command_event()
TextRotationMsg, EVT_COMMAND_TEXTROTATATION = new_command_event()

# Cell edit events

EditorShownMsg, EVT_COMMAND_EDITORSHOWN = new_command_event()
EditorHiddenMsg, EVT_COMMAND_EDITORHIDDEN = new_command_event()

# Cell selection events

CellSelectedMsg, EVT_COMMAND_CELLSELECTED = new_command_event()


# Grid
# ====

# File events

NewMsg, EVT_COMMAND_NEW = new_command_event()
OpenMsg, EVT_COMMAND_OPEN = new_command_event()
SaveMsg, EVT_COMMAND_SAVE = new_command_event()
SaveAsMsg, EVT_COMMAND_SAVEAS = new_command_event()
ImportMsg, EVT_COMMAND_IMPORT = new_command_event()
ExportMsg, EVT_COMMAND_EXPORT = new_command_event()
ApproveMsg, EVT_COMMAND_APPROVE = new_command_event()

# Print events

PageSetupMsg, EVT_COMMAND_PAGE_SETUP = new_command_event()
PrintPreviewMsg, EVT_COMMAND_PRINT_PREVIEW = new_command_event()
PrintMsg, EVT_COMMAND_PRINT = new_command_event()

# Clipboard events

CutMsg, EVT_COMMAND_CUT = new_command_event()
CopyMsg, EVT_COMMAND_COPY = new_command_event()
CopyResultMsg, EVT_COMMAND_COPY_RESULT = new_command_event()
PasteMsg, EVT_COMMAND_PASTE = new_command_event()

# Grid view events

RefreshSelectionMsg , EVT_COMMAND_REFRESH_SELECTION = new_command_event()
DisplayGotoCellDialogMsg , EVT_COMMAND_DISPLAY_GOTO_CELL_DIALOG = \
                                                    new_command_event()
GotoCellMsg , EVT_COMMAND_GOTO_CELL = new_command_event()
ZoomInMsg , EVT_COMMAND_ZOOM_IN = new_command_event()
ZoomOutMsg , EVT_COMMAND_ZOOM_OUT = new_command_event()
ZoomStandardMsg , EVT_COMMAND_ZOOM_STANDARD = new_command_event()

# Find events

FindMsg, EVT_COMMAND_FIND = new_command_event()
FindFocusMsg, EVT_COMMAND_FOCUSFIND = new_command_event()
ReplaceMsg, EVT_COMMAND_REPLACE = new_command_event()

# Grid change events

InsertRowsMsg, EVT_COMMAND_INSERT_ROWS = new_command_event()
InsertColsMsg, EVT_COMMAND_INSERT_COLS = new_command_event()
InsertTabsMsg, EVT_COMMAND_INSERT_TABS = new_command_event()
DeleteRowsMsg, EVT_COMMAND_DELETE_ROWS = new_command_event()
DeleteColsMsg, EVT_COMMAND_DELETE_COLS = new_command_event()
DeleteTabsMsg, EVT_COMMAND_DELETE_TABS = new_command_event()

ShowResizeGridDialogMsg, EVT_COMMAND_SHOW_RESIZE_GRID_DIALOG = \
                                                new_command_event()
ResizeGridMsg, EVT_COMMAND_RESIZE_GRID = new_command_event()

# Grid attribute events

# Undo/Redo events

UndoMsg, EVT_COMMAND_UNDO = new_command_event()
RedoMsg, EVT_COMMAND_REDO = new_command_event()


# Grid actions
# ============

# tuple dim
GridActionNewMsg, EVT_COMMAND_GRID_ACTION_NEW = new_command_event() 

# attr dict: keys: filepath: string, interface: object
GridActionOpenMsg, EVT_COMMAND_GRID_ACTION_OPEN = new_command_event() 
GridActionSaveMsg, EVT_COMMAND_GRID_ACTION_SAVE = new_command_event() 

GridActionTableSwitchMsg, EVT_COMMAND_GRID_ACTION_TABLE_SWITCH = \
                                                  new_command_event() 

# EntryLine
# =========

EntryLineMsg, EVT_ENTRYLINE_MSG = new_command_event()
##EntryLineSelectionMsg, EVT_ENTRYLINE_SELECTION_MSG = new_command_event()

# Statusbar
# =========

StatusBarMsg, EVT_STATUSBAR_MSG = wx.lib.newevent.NewEvent()
