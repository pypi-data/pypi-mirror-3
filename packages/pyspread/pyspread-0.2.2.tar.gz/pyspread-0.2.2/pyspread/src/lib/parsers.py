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
parsers
===========

Provides
--------

 * get_font_from_data
 * get_pen_from_data

"""

import wx

from src.sysvars import get_default_font


def get_font_from_data(fontdata):
    """Returns wx.Font from fontdata string"""

    textfont = get_default_font()

    if fontdata != "":
        nativefontinfo = wx.NativeFontInfo()
        nativefontinfo.FromString(fontdata)
        textfont.SetNativeFontInfo(nativefontinfo)

    return textfont


def get_pen_from_data(pendata):
    """Returns wx.Pen from pendata attribute list"""

    pen_color = wx.Colour()
    pen_color.SetRGB(pendata[0])
    pen = wx.Pen(pen_color, *pendata[1:])
    pen.SetJoin(wx.JOIN_MITER)

    return pen







