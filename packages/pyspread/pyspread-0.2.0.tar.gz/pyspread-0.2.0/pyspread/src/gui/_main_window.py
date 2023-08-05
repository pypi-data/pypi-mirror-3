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
_main_window
============

Provides:
---------
  1) MainWindow: Main window of the application pyspread

"""

import os

import wx
import wx.aui

import wx.lib.agw.genericmessagedialog as GMD

from src.config import config

from _menubars import MainMenu
from _toolbars import MainToolbar, FindToolbar, AttributesToolbar
from _widgets import EntryLine, StatusBar, TableChoiceIntCtrl

from src.lib.clipboard import Clipboard

from _gui_interfaces import GuiInterfaces
from src.gui.icons import icons

from _grid import Grid
from src.model.model import CodeArray

from _events import *

from src.actions._main_window_actions import AllMainWindowActions

class MainWindow(wx.Frame):
    """Main window of pyspread"""
    
    def __init__(self, parent, *args, **kwargs):
        wx.Frame.__init__(self, parent, *args, **kwargs)
        
        self.interfaces = GuiInterfaces(self)
        
        self._mgr = wx.aui.AuiManager(self)
    
        self.parent = parent
        
        self.handlers = MainWindowEventHandlers(self)
        
        # Program states
        # --------------
        
        self._states()
        
        # GUI elements
        # ------------
        
        # Menu Bar
        self.menubar = wx.MenuBar()
        self.main_menu = MainMenu(parent=self, menubar=self.menubar)
        self.SetMenuBar(self.menubar)
        
        # Disable menu item for leaving safe mode
        post_command_event(self, SafeModeExitMsg)
        
        # Status bar
        statusbar = StatusBar(self)
        self.SetStatusBar(statusbar)
        
        welcome_text = "Welcome to pyspread."
        post_command_event(self, StatusBarMsg, text=welcome_text)
        
        # Toolbars
        self.main_toolbar = MainToolbar(self, -1)
        self.find_toolbar = FindToolbar(self, -1)
        self.attributes_toolbar = AttributesToolbar(self, -1)
        
        # Entry line
        self.entry_line = EntryLine(self, style=wx.TE_PROCESS_ENTER)
        
        # Main grid
        
        dimensions = config["grid_shape"]
        self.grid = Grid(self, -1, dimensions=dimensions)

        # IntCtrl for table choice
        self.table_choice = TableChoiceIntCtrl(self, dimensions[2])

        # Clipboard
        self.clipboard = Clipboard()
        
        # Main window actions
        
        self.actions = AllMainWindowActions(self.grid)
        
        # Layout and bindings
        
        self._set_properties()
        self._do_layout()
        self._bind()
    
        
    def _states(self):
        """Sets main window states"""
        
        # Has the current file been changed since the last save?
        self.changed_since_save = False
        self.filepath = None
        
        # Print data
        
        self.print_data = wx.PrintData()
        # wx.PrintData properties setup from 
        # http://aspn.activestate.com/ASPN/Mail/Message/wxpython-users/3471083
    
    def _set_properties(self):
        """Setup title, icon, size, scale, statusbar, main grid"""
        
        self.set_icon(icons["PyspreadLogo"])
        
        # Set initial size to 90% of screen
        self.SetInitialSize(config["window_size"])
        self.SetPosition(config["window_position"])
        
        # Without minimum size, initial size is minimum size in wxGTK
        self.SetMinSize((2, 2))
        
        # Leave save mode
        post_command_event(self, SafeModeExitMsg)
        
        # Enable menu bar view item checkmarks
        toggles = ["Main toolbar", "Format toolbar", "Find toolbar", 
                   "Entry line", "Table choice"]
        for toggle in toggles:
            toggle_id = self.menubar.FindMenuItem("View", toggle)
            toggle_item = self.menubar.FindItemById(toggle_id)
            toggle_item.Check(True)
        
    def _do_layout(self):
        """Adds widgets to the wx.aui manager and controls the layout"""
        
        # Add the toolbars to the manager
        self._mgr.AddPane(self.main_toolbar, wx.aui.AuiPaneInfo().
                          Name("main_window_toolbar").Caption("Main Toolbar").
                          ToolbarPane().Top().Row(0).CloseButton(False).
                          LeftDockable(False).RightDockable(False))
                                  
        self._mgr.AddPane(self.find_toolbar, wx.aui.AuiPaneInfo().
                          Name("find_toolbar").Caption("Find").
                          ToolbarPane().Top().Row(1).MaximizeButton(False).
                          LeftDockable(False).RightDockable(False))
        
        self._mgr.AddPane(self.attributes_toolbar, wx.aui.AuiPaneInfo().
                          Name("attributes_toolbar").Caption("Cell Attributes").
                          ToolbarPane().Top().Row(1).MaximizeButton(False).
                          LeftDockable(False).RightDockable(False))
                          
                          
        self._mgr.AddPane(self.table_choice, wx.aui.AuiPaneInfo().
                          Name("table_choice").Caption("Table choice").
                          ToolbarPane().MaxSize((50, 50)).Row(2).
                          Top().CloseButton(False).MaximizeButton(False).
                          LeftDockable(True).RightDockable(True))
        
        self._mgr.AddPane(self.entry_line, wx.aui.AuiPaneInfo().
                          Name("entry_line").Caption("Entry line").
                          ToolbarPane().MinSize((10, 10)).Row(2).
                          Top().CloseButton(False).MaximizeButton(False).
                          LeftDockable(True).RightDockable(True))
        
        # Add the main grid
        self._mgr.AddPane(self.grid, wx.CENTER)
        
        # Tell the manager to 'commit' all the changes just made
        self._mgr.Update()
    
    def _bind(self):
        """Bind events to handlers"""
        
        handlers = self.handlers
        
        # Main window events
        self.Bind(wx.EVT_MOVE, handlers.OnMove)
        self.Bind(wx.EVT_SIZE, handlers.OnSize)
        
        # Content changed event, adjusts title bar with star
        self.Bind(EVT_CONTENT_CHANGED, handlers.OnContentChanged)
        
        # Program state events
        
        self.Bind(EVT_COMMAND_TITLE, handlers.OnTitle)
        self.Bind(EVT_COMMAND_SAFE_MODE_ENTRY, handlers.OnSafeModeEntry)
        self.Bind(EVT_COMMAND_SAFE_MODE_EXIT, handlers.OnSafeModeExit)
        self.Bind(wx.EVT_CLOSE, handlers.OnClose)
        self.Bind(EVT_COMMAND_CLOSE, handlers.OnClose)
        
        # Toolbar toggle events
        
        self.Bind(EVT_COMMAND_MAINTOOLBAR_TOGGLE, 
                  handlers.OnMainToolbarToggle)
        self.Bind(EVT_COMMAND_ATTRIBUTESTOOLBAR_TOGGLE, 
                  handlers.OnAttributesToolbarToggle)
        self.Bind(EVT_COMMAND_FIND_TOOLBAR_TOGGLE, 
                  handlers.OnFindToolbarToggle)
        self.Bind(EVT_COMMAND_ENTRYLINE_TOGGLE, 
                  handlers.OnEntryLineToggle)
        self.Bind(EVT_COMMAND_TABLECHOICE_TOGGLE, 
                  handlers.OnTableChoiceToggle)
        
        # File events
        
        self.Bind(EVT_COMMAND_NEW, handlers.OnNew)
        self.Bind(EVT_COMMAND_OPEN, handlers.OnOpen)
        self.Bind(EVT_COMMAND_SAVE, handlers.OnSave)
        self.Bind(EVT_COMMAND_SAVEAS, handlers.OnSaveAs)
        self.Bind(EVT_COMMAND_IMPORT, handlers.OnImport)
        self.Bind(EVT_COMMAND_EXPORT, handlers.OnExport)
        self.Bind(EVT_COMMAND_APPROVE, handlers.OnApprove)
        
        # Find events
        self.Bind(EVT_COMMAND_FOCUSFIND, handlers.OnFocusFind)
        
        # Print events
        
        self.Bind(EVT_COMMAND_PAGE_SETUP, handlers.OnPageSetup)
        self.Bind(EVT_COMMAND_PRINT_PREVIEW, handlers.OnPrintPreview)
        self.Bind(EVT_COMMAND_PRINT, handlers.OnPrint)
        
        # Clipboard events
        
        self.Bind(EVT_COMMAND_CUT, handlers.OnCut)
        self.Bind(EVT_COMMAND_COPY, handlers.OnCopy)
        self.Bind(EVT_COMMAND_COPY_RESULT, handlers.OnCopyResult)
        self.Bind(EVT_COMMAND_PASTE, handlers.OnPaste)
        
        # Help events
        
        self.Bind(EVT_COMMAND_MANUAL, handlers.OnManual)
        self.Bind(EVT_COMMAND_TUTORIAL, handlers.OnTutorial)
        self.Bind(EVT_COMMAND_FAQ, handlers.OnFaq)
        self.Bind(EVT_COMMAND_PYTHON_TURORIAL, handlers.OnPythonTutorial)
        self.Bind(EVT_COMMAND_ABOUT, handlers.OnAbout)
        
        self.Bind(EVT_COMMAND_MACROLIST, handlers.OnMacroList)
        self.Bind(EVT_COMMAND_MACROREPLACE, handlers.OnMacroReplace)
        self.Bind(EVT_COMMAND_MACROEXECUTE, handlers.OnMacroExecute)
        self.Bind(EVT_COMMAND_MACROLOAD, handlers.OnMacroListLoad)
        self.Bind(EVT_COMMAND_MACROSAVE, handlers.OnMacroListSave)
    
    def set_icon(self, bmp):
        """Sets main window icon to given wx.Bitmap"""
        
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(bmp)
        self.SetIcon(_icon)

    def get_safe_mode(self):
        """Returns safe_mode state from code_array"""
        
        return self.grid.code_array.safe_mode

    safe_mode = property(get_safe_mode)

# End of class MainWindow

class MainWindowEventHandlers(object):
    """Contains main window event handlers"""
    
    def __init__(self, parent):
        self.main_window = parent
        self.interfaces = parent.interfaces
    
    
    # Main window events
    
    def OnMove(self, event):
        """Main window move event"""
        
        # Store window position in config
        
        config["window_position"] = repr(event.GetPosition())
    
    def OnSize(self, event):
        """Main window move event"""
        
        # Store window position in config
        
        config["window_size"] = repr(event.GetSize())
    
    def OnContentChanged(self, event):
        """Titlebar star adjustment event handler"""
        
        self.main_window.changed_since_save = event.changed
        
        title = self.main_window.GetTitle()
        
        if event.changed:
            # Put * in front of title
            if title[:2] != "* ":
                new_title = "* " + title
                post_command_event(self.main_window, TitleMsg, text=new_title)
                
        elif title[:2] == "* ":
            # Remove * in front of title
            new_title = title[2:]
            post_command_event(self.main_window, TitleMsg, text=new_title)
    
    def OnTitle(self, event):
        """Title change event handler"""
        
        self.main_window.SetTitle(event.text)
    
    def OnSafeModeEntry(self, event):
        """Safe mode entry event handler"""
        
        # Enable menu item for leaving safe mode
        
        self.main_window.main_menu.enable_file_approve(True)
        
        self.main_window.grid.Refresh()
    
    def OnSafeModeExit(self, event):
        """Safe mode exit event handler"""
        
        # Run macros
        
        ##self.MainGrid.model.pysgrid.sgrid.execute_macros(safe_mode=False)
        
        # Disable menu item for leaving safe mode
        
        self.main_window.main_menu.enable_file_approve(False)
        
        self.main_window.grid.Refresh()
    
    def OnClose(self, event):
        """Program exit event handler"""
        
        # If changes have taken place save of old grid
        
        if self.main_window.changed_since_save:
            save_choice = self.interfaces.get_save_request_from_user()
            
            if save_choice is None:
                # Cancelled close operation
                return
                
            elif save_choice:
                # User wants to save content
                post_command_event(self.main_window, SaveMsg)
        
        # Uninit the AUI stuff
        
        self.main_window._mgr.UnInit()
        
        # Save config
        
        config.save()
        
        # Close main_window
        
        self.main_window.Destroy()
    
    # Toolbar events
    
    def _toggle_pane(self, pane):
        """Toggles visibility of given aui pane
        
        Parameters
        ----------
        
        pane: String
        \tPane name
        
        """
        
        if pane.IsShown():
            pane.Hide()
        else:
            pane.Show()
        
        self.main_window._mgr.Update()
   
    def OnMainToolbarToggle(self, event):
        """Standard toolbar toggle event handler"""
        
        main_toolbar = self.main_window._mgr.GetPane("main_window_toolbar")
        
        self._toggle_pane(main_toolbar)
        
        event.Skip()

    def OnAttributesToolbarToggle(self, event):
        """Format toolbar toggle event handler"""
        
        attributes_toolbar = self.main_window._mgr.GetPane("attributes_toolbar")
        
        self._toggle_pane(attributes_toolbar)
        
        event.Skip()
        
    def OnFindToolbarToggle(self, event):
        """Search toolbar toggle event handler"""
        
        find_toolbar = self.main_window._mgr.GetPane("find_toolbar")
        
        self._toggle_pane(find_toolbar)
        
        event.Skip()
        
    def OnEntryLineToggle(self, event):
        """Entry line toggle event handler"""
        
        entry_line = self.main_window._mgr.GetPane("entry_line")
        
        self._toggle_pane(entry_line)
        
        event.Skip()

    def OnTableChoiceToggle(self, event):
        """Table choice toggle event handler"""
        
        table_choice = self.main_window._mgr.GetPane("table_choice")
        
        self._toggle_pane(table_choice)
        
        event.Skip()

    # File events
    
    def OnNew(self, event):
        """New grid event handler"""
        
        # If changes have taken place save of old grid
        
        if self.main_window.changed_since_save:
            save_choice = self.interfaces.get_save_request_from_user()
            
            if save_choice is None:
                # Cancelled close operation
                return
                
            elif save_choice:
                # User wants to save content
                post_command_event(self.main_window, SaveMsg)
        
        # Get grid dimensions
        
        shape = self.interfaces.get_dimensions_from_user(no_dim=3)
        
        if shape is None:
            return
            
        self.main_window.grid.actions.change_grid_shape(shape)
        
        # Set new filepath and post it to the title bar
        
        self.main_window.filepath = None
        post_command_event(self.main_window, TitleMsg, text="pyspread")
        
        # Create new grid
        post_command_event(self.main_window, GridActionNewMsg, shape=shape)
        
        # Update TableChoiceIntCtrl
        post_command_event(self.main_window, ResizeGridMsg, shape=shape)
        
        self.main_window.grid.GetTable().ResetView()
        self.main_window.grid.ForceRefresh()
        
        # Display grid creation in status bar
        statustext = "New grid with dimensions " + str(shape) + " created."
        post_command_event(self.main_window, StatusBarMsg, text=statustext)
        
        self.main_window.grid.ForceRefresh()

    def OnOpen(self, event):
        """File open event handler"""
        
        # If changes have taken place save of old grid
        
        if self.main_window.changed_since_save:
            save_choice = self.interfaces.get_save_request_from_user()
            
            if save_choice is None:
                # Cancelled close operation
                return
                
            elif save_choice:
                # User wants to save content
                post_command_event(self.main_window, SaveMsg)
        
        # Get filepath from user
        
        wildcard = "Pyspread file (*.pys)|*.pys|" \
                   "All files (*.*)|*.*"
        message = "Choose pyspread file to open."
        style = wx.OPEN | wx.CHANGE_DIR
        filepath, filterindex = self.interfaces.get_filepath_findex_from_user( \
                                    wildcard, message, style)
        
        if filepath is None:
            return
        
        # Change the main window filepath state
        
        self.main_window.filepath = filepath
            
        # Load file into grid
        
        post_command_event(self.main_window, GridActionOpenMsg, 
                           attr={"filepath": filepath})
        
        # Set Window title to new filepath
        
        title_text = filepath.split("/")[-1] + " - pyspread"
        post_command_event(self.main_window, TitleMsg, text=title_text)
        
        # Display file load in status bar
        
        statustext = "File " + filepath + " loaded."
        post_command_event(self.main_window, StatusBarMsg, text=statustext)
        
        self.main_window.grid.ForceRefresh()
    
    def OnSave(self, event):
        """File save event handler"""
        
        # If there is no filepath then jump to save as
        
        if self.main_window.filepath is None:
            post_command_event(self.main_window, SaveAsMsg)
            return
        
        # Save the grid
        
        post_command_event(self.main_window, GridActionSaveMsg, 
                           attr={"filepath": self.main_window.filepath})
        
        # Display file save in status bar
        
        statustext = self.main_window.filepath.split("/")[-1] + " saved."
        post_command_event(self.main_window, StatusBarMsg, text=statustext)
    
    def OnSaveAs(self, event):
        """File save as event handler"""
        
        # Get filepath from user
        
        wildcard = "Pyspread file (*.pys)|*.pys|" \
                   "All files (*.*)|*.*"
        message = "Choose filename for saving."
        style = wx.SAVE | wx.CHANGE_DIR
        filepath, filterindex = self.interfaces.get_filepath_findex_from_user( \
                                    wildcard, message, style)
        
        if filepath is not None:
            
            # Look if path is already present
            if os.path.exists(filepath):
                if os.path.isfile(filepath):
                    # There is a file with the same path
                    message = "The file " + filepath + \
                              " is already present.\nOverwrite?"
                    short_message = "File collison"
                    if not self.main_window.interfaces.get_warning_choice( \
                                message, short_message):
                        
                        statustext = "File present. Save aborted by user."
                        post_command_event(self.main_window, StatusBarMsg, 
                                       text=statustext)
                        return 0
                else:
                    # There is a directory with the same path
                    statustext = "Directory present. Save aborted."
                    post_command_event(self.main_window, StatusBarMsg, 
                                       text=statustext)
                    return 0
            
            # Put pys suffix if wildcard choice is 0
            
            if filterindex == 0 and filepath[-4:] != ".pys":
                filepath += ".pys"
            
            # Set the filepath state
            
            self.main_window.filepath = filepath
            
            # Set Window title to new filepath
        
            title_text = filepath.split("/")[-1] + " - pyspread"
            post_command_event(self.main_window, TitleMsg, text=title_text)
            
            # Now jump to save
            
            post_command_event(self.main_window, SaveMsg)
                
    def OnImport(self, event):
        """File import event handler"""
        
        # Get filepath from user
        
        wildcard = wildcard="Csv file (*.*)|*.*|" \
                            "Tab delimited text file (*.*)|*.*"
        message = "Choose file to import."
        style = wx.OPEN | wx.CHANGE_DIR
        filepath, filterindex = self.interfaces.get_filepath_findex_from_user( \
                                    wildcard, message, style)
        
        if filepath is None:
            return
        
        # Get generator of import data
        import_data = self.main_window.actions.import_file(filepath, 
                                                           filterindex)
        
        if import_data is None:
            return
        
        # Paste import data to grid
        grid = self.main_window.grid
        tl_cell = grid.GetGridCursorRow(), grid.GetGridCursorCol()
        
        grid.actions.paste(tl_cell, import_data)
        
        self.main_window.grid.ForceRefresh()
        
    def OnExport(self, event):
        """File export event handler
        
        Currently, only CSV export is supported
        
        """
        
        selection = self.main_window.grid.selection
        
        # Check if no selection is present
        
        selection_bbox = selection.get_bbox()
        
        if selection_bbox is None:
            # No selection --> Use current screen
            
            selection_bbox = self.main_window.grid.actions.get_visible_area()
        
        (top, left), (bottom, right) = selection_bbox
        
        # Generator of row and column keys in correct order
        
        code_array = self.main_window.grid.code_array
        tab = self.main_window.grid.current_table
        
        data = code_array[top:bottom+1, left:right+1, tab]
        
        # Get target filepath from user
        
        wildcard = wildcard=" CSV file (*.*)|*.*"
        message = "Choose filename for export."
        style = wx.OPEN | wx.CHANGE_DIR
        path, filterindex = self.interfaces.get_filepath_findex_from_user( \
                                    wildcard, message, style)
        
        # Export file
        # -----------
        
        self.main_window.actions.export_file(path, filterindex, data)
    
    def OnApprove(self, event):
        """File approve event handler"""
        
        if not self.main_window.safe_mode:
            return
        
        msg = u"You are going to approve and trust a file that\n" + \
              u"you have received from an untrusted source.\n" + \
              u"After proceeding, the file is executed.\n" + \
              u"It can harm your system as any program can.\n" + \
              u"Unless you took precautions, it can delete your\n" + \
              u"files or send them away over the Internet.\n" + \
              u"CHECK EACH CELL BEFORE PROCEEDING.\n \n" + \
              u"Do not forget cells outside the visible range.\n" + \
              u"You have been warned.\n \n" + \
              u"Proceed and sign this file as trusted?"
            
        short_msg = "Security warning"
        
        if self.main_window.interfaces.get_warning_choice(msg, short_msg):
            # Leave safe mode
            self.main_window.grid.actions.leave_safe_mode()
            
            # Display safe mode end in status bar
        
            statustext = "Safe mode deactivated."
            post_command_event(self.main_window, StatusBarMsg, text=statustext)
    
    # Print events
    
    def OnPageSetup(self, event):
        """Page setup handler for printing framework"""
        
        print_data = self.main_window.print_data
        new_print_data = self.main_window.interfaces.get_print_setup(print_data)
        self.main_window.print_data = new_print_data

    
    def _get_print_area(self):
        """Returns selection bounding box or visible area"""
        
        # Get print area from current selection
        selection = self.main_window.grid.selection
        print_area = selection.get_bbox()
        
        # If there is no selection use the visible area on the screen
        if print_area is None:
            print_area = self.main_window.grid.actions.get_visible_area()
        
        return print_area
    
    def OnPrintPreview(self, event):
        """Print preview handler"""
        
        print_area = self._get_print_area()
        print_data = self.main_window.print_data
        
        self.main_window.actions.print_preview(print_area, print_data)
    
    def OnPrint(self, event):
        """Print event handler"""
        
        print_area = self._get_print_area()
        print_data = self.main_window.print_data
        
        self.main_window.actions.printout(print_area, print_data)
    
    # Clipboard events

    def OnCut(self, event): 
        """Clipboard cut event handler"""
        
        data = self.main_window.actions.cut(self.main_window.grid.selection)
        self.main_window.clipboard.set_clipboard(data)
        
        self.main_window.grid.ForceRefresh()
        
        event.Skip()
    
    def OnCopy(self, event):
        """Clipboard copy event handler"""
        
        data = self.main_window.actions.copy(self.main_window.grid.selection)
        self.main_window.clipboard.set_clipboard(data)
        
        event.Skip()
    
    def OnCopyResult(self, event):
        """Clipboard copy results event handler"""
        
        data = self.main_window.actions.copy_result( \
                            self.main_window.grid.selection)
        self.main_window.clipboard.set_clipboard(data)
        
        event.Skip()
    
    def OnPaste(self, event):
        """Clipboard paste event handler"""
        
        focus = self.main_window.FindFocus()
        
        if isinstance(focus, wx.TextCtrl):
            pass
        else: # We got a grid selection
            grid = self.main_window.grid
            key = (grid.GetGridCursorRow(), \
                   grid.GetGridCursorCol(), \
                   grid.current_table)
                   
            data = self.main_window.clipboard.get_clipboard()
        
            self.main_window.actions.paste(key, data)
        
        self.main_window.grid.ForceRefresh()
        
        event.Skip()
    
    # View events
    
    def OnFocusFind(self, event):
        """Event handler for focusing find toolbar text widget"""
        
        self.main_window.find_toolbar.search.SetFocus()
    
    # Macro events
    
    def OnMacroList(self, event):
        """Macro list dialog event handler"""
        
        self.main_window.interfaces.display_macros()
        
        event.Skip()
    
    def OnMacroReplace(self, event):
        """Macro change event handler"""
        
        self.main_window.actions.replace_macros(event.macros)
    
    def OnMacroExecute(self, event):
        """Macro execution event handler"""
        
        self.main_window.actions.execute_macros()
    
    def OnMacroListLoad(self, event): 
        """Macro list load event handler"""
        
        # Get filepath from user
        
        wildcard = "Macro file (*.py)|*.py|" \
                   "All files (*.*)|*.*"
        message = "Choose macro file."
        
        style = wx.OPEN | wx.CHANGE_DIR
        filepath, filterindex = self.interfaces.get_filepath_findex_from_user( \
                                    wildcard, message, style)
        
        if filepath is None:
            return
        
        # Enter safe mode because macro file could be harmful
        
        post_command_event(self.main_window, SafeModeEntryMsg)
        
        # Load macros from file
        
        self.main_window.actions.open_macros(filepath)
        
        event.Skip()
    
    def OnMacroListSave(self, event):
        """Macro list save event handler"""
        
        # Get filepath from user
        
        wildcard = "Macro file (*.py)|*.py|" \
                   "All files (*.*)|*.*"
        message = "Choose macro file."
        
        style = wx.SAVE | wx.CHANGE_DIR
        filepath, filterindex = self.interfaces.get_filepath_findex_from_user( \
                                    wildcard, message, style)
        
        # Save macros to file
        
        macros = self.main_window.grid.code_array.macros
        self.main_window.actions.save_macros(filepath, macros)
        
        event.Skip()
    
    # Help events
    
    def OnManual(self, event):
        """Manual launch event handler"""
        
        self.main_window.actions.launch_help("First steps in pyspread", 
            "First steps in pyspread.html")
    
    def OnTutorial(self, event):
        """Tutorial launch event handler"""
        
        self.main_window.actions.launch_help("Pyspread tutorial", 
                                             "tutorial.html")
        
    def OnFaq(self, event):
        """FAQ launch event handler"""
        
        self.main_window.actions.launch_help("Pyspread tutorial", "faq.html")

    def OnPythonTutorial(self, event):
        """Python tutorial launch event handler"""
        
        self.main_window.actions.launch_help("Python tutorial", 
            "http://docs.python.org/tutorial/")
    
    
    def OnAbout(self, event):
        """About dialog event handler"""
        
        self.main_window.interfaces.display_about(self.main_window)
    
# End of class MainWindowEventHandlers
