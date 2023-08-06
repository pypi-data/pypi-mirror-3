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
_toolbars
===========

Provides toolbars

Provides:
---------
  1. MainToolbar: Main toolbar of pyspread
  2. FindToolbar: Toolbar for Find operation
  3. AttributesToolbar: Toolbar for editing cell attributes

"""

import i18n

import wx
import wx.lib.colourselect as csel

from _events import post_command_event, EventMixin

from src.config import config
from src.sysvars import get_default_font, get_font_list
from icons import icons

import _widgets

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class MainToolbar(wx.ToolBar, EventMixin):
    """Main application toolbar, built from attribute toolbardata

    toolbardata has the following structure:
    [["Methodname", "Label", "Iconname", "Tooltip", "Help string"] , \
    ...
    [] ,\  # Separator
    ...
    ]

    """

    def __init__(self, *args, **kwargs):
        wx.ToolBar.__init__(self, *args, **kwargs)

        self.toolbardata = [
            [self.NewMsg, _("New"), "FileNew", _("New spreadsheet"),
                _("Create a new, empty spreadsheet")], \
            [self.OpenMsg, _("Open"), "FileOpen", _("Open spreadsheet"),
                _("Open spreadsheet from file")], \
            [self.SaveMsg, _("Save"), "FileSave", _("Save spreadsheet"),
                _("Save spreadsheet to file")], \
            [], \
            [self.UndoMsg, _("Undo"), "Undo", _("Undo"),
                 _("Undo last operation")], \
            [self.RedoMsg, _("Redo"), "Redo", _("Redo"),
                 _("Redo next operation")], \
            [], \
            [self.FindFocusMsg, _("Find"), "Find", _("Find"),
                _("Find cell by content")], \
            [self.ReplaceMsg, _("Replace"), "FindReplace", _("Replace"),
                _("Replace strings in cells")], \
            [], \
            [self.CutMsg, _("Cut"), "EditCut", _("Cut"),
                 _("Cut cells to clipboard")], \
            [self.CopyMsg, _("Copy"), "EditCopy", _("Copy"),
                _("Copy the input strings of the cells to clipboard")], \
            [self.CopyResultMsg, _("Copy Results"), "EditCopyRes",
                 _("Copy Results"),
                _("Copy the result strings of the cells to the clipboard")], \
            [self.PasteMsg, _("Paste"), "EditPaste", _("Paste"),
                _("Paste cell from clipboard")], \
            [], \
            [self.PrintMsg, _("Print"), "FilePrint",
                 _("Print current spreadsheet"),
                 _("Print current spreadsheet")],
        ]

        self.SetToolBitmapSize(icons.icon_size)

        self.ids_msgs = {}

        self.parent = args[0]
        self._add_tools()

    def _add_tools(self):
        """Adds tools from self.toolbardata to self"""

        for tool in self.toolbardata:
            if tool:
                msgtype, label, icon_name, tooltip, helpstring = tool
                icon = icons[icon_name]
                toolid = wx.NewId()
                self.AddLabelTool(toolid, label, icon, wx.NullBitmap,
                                  wx.ITEM_NORMAL, tooltip, helpstring)

                self.ids_msgs[toolid] = msgtype

                self.parent.Bind(wx.EVT_TOOL, self.OnTool, id=toolid)

            else:
                self.AddSeparator()

    def OnTool(self, event):
        """Toolbar event handler"""

        msgtype = self.ids_msgs[event.GetId()]
        post_command_event(self, msgtype)

# end of class MainToolbar


class FindToolbar(wx.ToolBar, EventMixin):
    """Toolbar for find operations (replaces wxFindReplaceDialog)"""

    # Search flag buttons
    search_options_buttons = { \
      "matchcase_tb": { \
        "ID": wx.NewId(),
        "iconname": "SearchCaseSensitive",
        "shorthelp": _("Case sensitive"),
        "longhelp": _("Case sensitive search"),
        "flag": "MATCH_CASE",
      },
      "regexp_tb": {
        "ID": wx.NewId(),
        "iconname": "SearchRegexp",
        "shorthelp": _("Regular expression"),
        "longhelp": _("Treat search string as regular expression"),
        "flag": "REG_EXP",
      },
      "wholeword_tb": { \
        "ID": wx.NewId(),
        "iconname": "SearchWholeword",
        "shorthelp": _("Whole word"),
        "longhelp": _("Search string is surronted by whitespace characters"),
        "flag": "WHOLE_WORD",
      },
    }

    def __init__(self, parent, *args, **kwargs):
        kwargs["style"] = wx.TB_FLAT | wx.TB_NODIVIDER
        wx.ToolBar.__init__(self, parent, *args, **kwargs)

        self.SetToolBitmapSize(icons.icon_size)

        self.parent = parent

        # Search entry control
        self.search_history = []
        self.search = wx.SearchCtrl(self, size=(150, -1), \
                        style=wx.TE_PROCESS_ENTER | wx.NO_BORDER)
        tip_msg = _("Searches in grid cell source code and grid cell results.")
        self.search.SetToolTip(wx.ToolTip(tip_msg))
        self.menu = self.make_menu()
        self.search.SetMenu(self.menu)
        self.AddControl(self.search)

        # Search direction toggle button
        self.search_options = ["DOWN"]
        self.setup_searchdirection_togglebutton()

        # Search flags buttons
        sfbs = self.search_options_buttons
        for name in sfbs:
            iconname = sfbs[name]["iconname"]
            __id = sfbs[name]["ID"]
            shorthelp = sfbs[name]["shorthelp"]
            longhelp = sfbs[name]["longhelp"]

            bmp = icons[iconname]
            self.AddCheckLabelTool(__id, name, bmp,
                shortHelp=shorthelp, longHelp=longhelp)

        # Event bindings
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.search)
        self.Bind(wx.EVT_MENU_RANGE, self.OnSearchFlag)
        self.Bind(wx.EVT_BUTTON, self.OnSearchDirectionButton,
                                 self.search_direction_tb)
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Realize()

    def setup_searchdirection_togglebutton(self):
        """Setup of search direction toggle button for searching up and down"""

        iconnames = ["SearchDirectionDown", "SearchDirectionUp"]
        bmplist = [icons[iconname] for iconname in iconnames]
        self.search_direction_tb = _widgets.BitmapToggleButton(self, bmplist)

        self.search_direction_tb.SetInitialSize()
        self.search_direction_tb.SetToolTip(wx.ToolTip(_("Search direction")))
        self.AddControl(self.search_direction_tb)

    def make_menu(self):
        """Creates the search menu"""

        menu = wx.Menu()
        item = menu.Append(-1, "Recent Searches")
        item.Enable(False)

        for __id, txt in enumerate(self.search_history):
            menu.Append(__id, txt)
        return menu

    def OnMenu(self, event):
        """Search history has been selected"""

        __id = event.GetId()
        try:
            menuitem = event.GetEventObject().FindItemById(__id)
            selected_text = menuitem.GetItemLabel()
            self.search.SetValue(selected_text)
        except AttributeError:
            # Not called by menu
            event.Skip()

    def OnSearch(self, event):
        """Event handler for starting the search"""

        search_string = self.search.GetValue()

        if search_string not in self.search_history:
            self.search_history.append(search_string)
        if len(self.search_history) > 10:
            self.search_history.pop(0)

        self.menu = self.make_menu()
        self.search.SetMenu(self.menu)

        search_flags = self.search_options + ["FIND_NEXT"]

        post_command_event(self, self.FindMsg, text=search_string,
                           flags=search_flags)

        self.search.SetFocus()

    def OnSearchDirectionButton(self, event):
        """Event handler for search direction toggle button"""

        if "DOWN" in self.search_options:
            flag_index = self.search_options.index("DOWN")
            self.search_options[flag_index] = "UP"
        elif "UP" in self.search_options:
            flag_index = self.search_options.index("UP")
            self.search_options[flag_index] = "DOWN"
        else:
            raise AttributeError(_("Neither UP nor DOWN in search_flags"))

        event.Skip()

    def OnSearchFlag(self, event):
        """Event handler for search flag toggle buttons"""

        sfbs = self.search_options_buttons
        for name in sfbs:
            if sfbs[name]["ID"] == event.GetId():
                if event.IsChecked():
                    self.search_options.append(sfbs[name]["flag"])
                else:
                    flag_index = self.search_options.index(sfbs[name]["flag"])
                    self.search_options.pop(flag_index)
        event.Skip()

# end of class FindToolbar


class AttributesToolbar(wx.ToolBar, EventMixin):
    """Toolbar for editing cell attributes

    Class attributes
    ----------------

    border_toggles: Toggles for border changes, points to
                    (top, bottom, left, right, inner, outer)
    bordermap: Meaning of each border_toggle item

    """

    border_toggles = [ \
        ("AllBorders",       (1, 1, 1, 1, 1, 1)),
        ("LeftBorders",      (0, 0, 1, 0, 1, 1)),
        ("RightBorders",     (0, 0, 0, 1, 1, 1)),
        ("TopBorders",       (1, 0, 0, 0, 1, 1)),
        ("BottomBorders",    (0, 1, 0, 0, 1, 1)),
        ##("InsideBorders",    (1, 1, 1, 1, 1, 0)),
        ("OutsideBorders",   (1, 1, 1, 1, 0, 1)),
        ("TopBottomBorders", (1, 1, 0, 0, 0, 1)),
    ]

    bordermap = { \
        "AllBorders":       ("top", "bottom", "left", "right", "inner"),
        "LeftBorders":      ("left"),
        "RightBorders":     ("right"),
        "TopBorders":       ("top"),
        "BottomBorders":    ("bottom"),
        ##"InsideBorders":    ("inner"),
        "OutsideBorders":   ("top", "bottom", "left", "right"),
        "TopBottomBorders": ("top", "bottom"),
    }

    def __init__(self, parent, *args, **kwargs):
        kwargs["style"] = wx.TB_FLAT | wx.TB_NODIVIDER
        wx.ToolBar.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.SetToolBitmapSize(icons.icon_size)

        self._create_font_choice_combo()
        self._create_font_size_combo()
        self._create_font_face_buttons()
        self._create_justification_button()
        self._create_alignment_button()
        self._create_borderchoice_combo()
        self._create_penwidth_combo()
        self._create_color_buttons()
        self._create_textrotation_spinctrl()

        self.Realize()

    # Create toolbar widgets
    # ----------------------

    def _create_font_choice_combo(self):
        """Creates font choice combo box"""

        self.fonts = get_font_list()
        self.font_choice_combo = _widgets.FontChoiceCombobox(self, \
                                    choices=self.fonts, style=wx.CB_READONLY,
                                    size=(125, -1))
        self.AddControl(self.font_choice_combo)

        self.Bind(wx.EVT_COMBOBOX, self.OnTextFont, self.font_choice_combo)
        self.parent.Bind(self.EVT_CMD_TOOLBAR_UPDATE, self.OnUpdate)

    def _create_font_size_combo(self):
        """Creates font size combo box"""

        self.std_font_sizes = config["font_default_sizes"]
        font_size = str(get_default_font().GetPointSize())
        self.font_size_combo = wx.ComboBox(self, -1, value=font_size,
            size=(60, -1), choices=map(unicode, self.std_font_sizes),
            style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
        self.AddControl(self.font_size_combo)
        self.Bind(wx.EVT_COMBOBOX, self.OnTextSize, self.font_size_combo)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextSize, self.font_size_combo)

    def _create_font_face_buttons(self):
        """Creates font face buttons"""

        font_face_buttons = [
            (wx.FONTFLAG_BOLD, "OnBold", "FormatTextBold", _("Bold")),
            (wx.FONTFLAG_ITALIC, "OnItalics", "FormatTextItalic",
                 _("Italics")),
            (wx.FONTFLAG_UNDERLINED, "OnUnderline", "FormatTextUnderline",
                _("Underline")),
            (wx.FONTFLAG_STRIKETHROUGH, "OnStrikethrough",
                "FormatTextStrikethrough", _("Strikethrough")),
            (wx.FONTFLAG_MASK, "OnFreeze", "Freeze", _("Freeze")),
        ]

        for __id, method, iconname, helpstring in font_face_buttons:
            bmp = icons[iconname]
            self.AddCheckLabelTool(__id, "", bmp, shortHelp=helpstring)
            self.Bind(wx.EVT_TOOL, getattr(self, method), id=__id)

    def _create_justification_button(self):
        """Creates horizontal justification button"""

        iconnames = ["JustifyLeft", "JustifyCenter", "JustifyRight"]
        bmplist = [icons[iconname] for iconname in iconnames]
        self.justify_tb = _widgets.BitmapToggleButton(self, bmplist)
        self.Bind(wx.EVT_BUTTON, self.OnJustification, self.justify_tb)
        self.AddControl(self.justify_tb)

    def _create_alignment_button(self):
        """Creates vertical alignment button"""

        iconnames = ["AlignTop", "AlignCenter", "AlignBottom"]
        bmplist = [icons[iconname] for iconname in iconnames]

        self.alignment_tb = _widgets.BitmapToggleButton(self, bmplist)
        self.Bind(wx.EVT_BUTTON, self.OnAlignment, self.alignment_tb)
        self.AddControl(self.alignment_tb)

    def _create_borderchoice_combo(self):
        """Create border choice combo box"""

        choices = [c[0] for c in self.border_toggles]
        self.borderchoice_combo = _widgets.BorderEditChoice(self,
                 choices=choices, style=wx.CB_READONLY, size=(50, -1))

        self.borderstate = self.border_toggles[0][0]

        self.AddControl(self.borderchoice_combo)

        self.Bind(wx.EVT_COMBOBOX, self.OnBorderChoice,
                  self.borderchoice_combo)

        self.borderchoice_combo.SetValue("AllBorders")

    def _create_penwidth_combo(self):
        """Create pen width combo box"""

        choices = map(unicode, xrange(12))
        self.pen_width_combo = _widgets.PenWidthComboBox(self,
                choices=choices, style=wx.CB_READONLY, size=(50, -1))

        self.AddControl(self.pen_width_combo)
        self.Bind(wx.EVT_COMBOBOX, self.OnLineWidth, self.pen_width_combo)

    def _create_color_buttons(self):
        """Create color choice buttons"""

        button_size = (30, 30)
        button_style = wx.NO_BORDER

        try:
            self.linecolor_choice = \
                csel.ColourSelect(self, -1, unichr(0x2500), (0, 0, 0),
                                  size=button_size, style=button_style)
        except UnicodeEncodeError:
            # ANSI wxPython installed
            self.linecolor_choice = \
                csel.ColourSelect(self, -1, "-", (0, 0, 0),
                                  size=button_size, style=button_style)

        self.bgcolor_choice = \
            csel.ColourSelect(self, -1, "", (255, 255, 255),
                              size=button_size, style=button_style)
        self.textcolor_choice = \
            csel.ColourSelect(self, -1, "A", (0, 0, 0),
                              size=button_size, style=button_style)

        self.AddControl(self.linecolor_choice)
        self.AddControl(self.bgcolor_choice)
        self.AddControl(self.textcolor_choice)

        self.linecolor_choice.Bind(csel.EVT_COLOURSELECT, self.OnLineColor)
        self.bgcolor_choice.Bind(csel.EVT_COLOURSELECT, self.OnBGColor)
        self.textcolor_choice.Bind(csel.EVT_COLOURSELECT, self.OnTextColor)

    def _create_textrotation_spinctrl(self):
        """Create text rotation spin control"""

        self.rotation_spinctrl = wx.SpinCtrl(self, -1, "", size=(50, -1))
        self.rotation_spinctrl.SetRange(-179, 180)
        self.rotation_spinctrl.SetValue(0)

        # For compatibility with toggle buttons
        self.rotation_spinctrl.GetToolState = lambda x: None

        self.AddControl(self.rotation_spinctrl)

        self.Bind(wx.EVT_SPINCTRL, self.OnRotate, self.rotation_spinctrl)

    # Update widget state methods
    # ---------------------------

    def _update_font(self, textfont):
        """Updates text font widget

        Parameters
        ----------

        textfont: String
        \tFont name

        """

        try:
            fontface_id = self.fonts.index(textfont)
        except ValueError:
            fontface_id = 0

        self.font_choice_combo.Select(fontface_id)

    def _update_pointsize(self, pointsize):
        """Updates text size widget

        Parameters
        ----------

        pointsize: Integer
        \tFont point size

        """

        self.font_size_combo.SetValue(str(pointsize))

    def _update_font_weight(self, font_weight):
        """Updates font weight widget

        Parameters
        ----------

        font_weight: Integer
        \tButton down iif font_weight == wx.FONTWEIGHT_BOLD

        """

        toggle_state = font_weight == wx.FONTWEIGHT_BOLD

        self.ToggleTool(wx.FONTFLAG_BOLD, toggle_state)

    def _update_font_style(self, font_style):
        """Updates font style widget

        Parameters
        ----------

        font_style: Integer
        \tButton down iif font_style == wx.FONTSTYLE_ITALIC

        """

        toggle_state = font_style == wx.FONTSTYLE_ITALIC

        self.ToggleTool(wx.FONTFLAG_ITALIC, toggle_state)

    def _update_frozencell(self, frozen):
        """Updates frozen cell widget

        Parameters
        ----------

        frozen: Bool or string
        \tUntoggled iif False

        """

        toggle_state = not frozen is False

        self.ToggleTool(wx.FONTFLAG_MASK, toggle_state)

    def _update_underline(self, underlined):
        """Updates underline widget

        Parameters
        ----------

        underlined: Bool
        \tToggle state

        """

        self.ToggleTool(wx.FONTFLAG_UNDERLINED, underlined)

    def _update_strikethrough(self, strikethrough):
        """Updates text strikethrough widget

        Parameters
        ----------

        strikethrough: Bool
        \tToggle state

        """

        self.ToggleTool(wx.FONTFLAG_STRIKETHROUGH, strikethrough)

    def _update_justification(self, justification):
        """Updates horizontal text justification button

        Parameters
        ----------

        justification: String in ["left", "center", "right"]
        \tSwitches button to untoggled if False and toggled if True

        """

        states = {"left": 2, "center": 0, "right": 1}

        self.justify_tb.state = states[justification]

        self.justify_tb.toggle(None)
        self.justify_tb.Refresh()

    def _update_alignment(self, alignment):
        """Updates vertical text alignment button

        Parameters
        ----------

        alignment: String in ["top", "middle", "right"]
        \tSwitches button to untoggled if False and toggled if True

        """

        states = {"top": 2, "middle": 0, "bottom": 1}

        self.alignment_tb.state = states[alignment]

        self.alignment_tb.toggle(None)
        self.alignment_tb.Refresh()

    def _update_fontcolor(self, fontcolor):
        """Updates text font color button

        Parameters
        ----------

        fontcolor: Integer
        \tText color in integer RGB format

        """

        textcolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT)
        textcolor.SetRGB(fontcolor)

        self.textcolor_choice.SetColour(textcolor)

    def _update_textrotation(self, angle):
        """Updates text rotation spin control"""

        self.rotation_spinctrl.SetValue(angle)

    def _update_bgbrush(self, bgcolor):
        """Updates background color"""

        brush_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)
        brush_color.SetRGB(bgcolor)

        self.bgcolor_choice.SetColour(brush_color)

    def _update_bordercolor(self, bordercolor):
        """Updates background color"""

        border_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVEBORDER)
        border_color.SetRGB(bordercolor)

        self.linecolor_choice.SetColour(border_color)

    def _update_borderwidth(self, borderwidth):
        """Updates background color"""

        self.pen_width_combo.SetSelection(borderwidth)

    # Attributes toolbar event handlers
    # ---------------------------------

    def OnUpdate(self, event):
        """Updates the toolbar states"""

        wx.Yield()

        attributes = event.attr

        self._update_font(attributes["textfont"])
        self._update_pointsize(attributes["pointsize"])
        self._update_font_weight(attributes["fontweight"])
        self._update_font_style(attributes["fontstyle"])
        self._update_frozencell(attributes["frozen"])
        self._update_underline(attributes["underline"])
        self._update_strikethrough(attributes["strikethrough"])
        self._update_justification(attributes["justification"])
        self._update_alignment(attributes["vertical_align"])
        self._update_fontcolor(attributes["textcolor"])
        self._update_textrotation(attributes["angle"])
        self._update_bgbrush(attributes["bgcolor"])
        self._update_bordercolor(attributes["bordercolor_bottom"])
        self._update_borderwidth(attributes["borderwidth_bottom"])

    def OnBorderChoice(self, event):
        """Change the borders that are affected by color and width changes"""

        choicelist = event.GetEventObject().GetItems()
        self.borderstate = choicelist[event.GetInt()]

    def OnLineColor(self, event):
        """Line color choice event handler"""

        color = event.GetValue().GetRGB()
        borders = self.bordermap[self.borderstate]

        post_command_event(self, self.BorderColorMsg, color=color,
                           borders=borders)

    def OnLineWidth(self, event):
        """Line width choice event handler"""

        linewidth_combobox = event.GetEventObject()
        idx = event.GetInt()
        width = int(linewidth_combobox.GetString(idx))
        borders = self.bordermap[self.borderstate]

        post_command_event(self, self.BorderWidthMsg, width=width,
                           borders=borders)

    def OnBGColor(self, event):
        """Background color choice event handler"""

        color = event.GetValue().GetRGB()

        post_command_event(self, self.BackgroundColorMsg, color=color)

    def OnTextColor(self, event):
        """Text color choice event handler"""

        color = event.GetValue().GetRGB()

        post_command_event(self, self.TextColorMsg, color=color)

    def OnTextFont(self, event):
        """Text font choice event handler"""

        fontchoice_combobox = event.GetEventObject()
        idx = event.GetInt()

        try:
            font_string = fontchoice_combobox.GetString(idx)
        except AttributeError:
            font_string = event.GetString()

        post_command_event(self, self.FontMsg, font=font_string)

    def OnTextSize(self, event):
        """Text size combo text event handler"""

        try:
            size = int(event.GetString())

        except Exception:
            size = get_default_font().GetPointSize()

        post_command_event(self, self.FontSizeMsg, size=size)

    def OnBold(self, event):
        """Bold toggle button event handler"""

        post_command_event(self, self.FontBoldMsg)

    def OnItalics(self, event):
        """Bold toggle button event handler"""

        post_command_event(self, self.FontItalicsMsg)

    def OnUnderline(self, event):
        """Bold toggle button event handler"""

        post_command_event(self, self.FontUnderlineMsg)

    def OnStrikethrough(self, event):
        """Bold toggle button event handler"""

        post_command_event(self, self.FontStrikethroughMsg)

    def OnFreeze(self, event):
        """Bold toggle button event handler"""

        post_command_event(self, self.FrozenMsg)

    def OnJustification(self, event):
        """Justification toggle button event handler"""

        post_command_event(self, self.JustificationMsg)

    def OnAlignment(self, event):
        """Alignment toggle button event handler"""

        post_command_event(self, self.AlignmentMsg)

    def OnRotate(self, event):
        """Rotation spin control event handler"""

        angle = self.rotation_spinctrl.GetValue()

        post_command_event(self, self.TextRotationMsg, angle=angle)

# end of class AttributesToolbar