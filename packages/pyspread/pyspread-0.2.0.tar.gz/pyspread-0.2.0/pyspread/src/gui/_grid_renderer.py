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
_grid_renderer
==============

Provides
--------

1) TextRenderer: Draws the grid
2) Background: Background drawing

"""

from math import pi, sin, cos
import types

import wx.grid

import src.lib.xrect as xrect

from src.lib.parsers import get_pen_from_data, get_font_from_data

from src.config import config

class GridRenderer(wx.grid.PyGridCellRenderer):
    """This renderer draws borders and text at specified font, size, color"""

    def __init__(self, data_array):
        
        wx.grid.PyGridCellRenderer.__init__(self)
        
        self.data_array = data_array
        
        # Background key is (width, height, bgbrush, 
        # borderwidth_bottom, borderwidth_right, 
        # bordercolor_bottom, bordercolor_right)
        self.backgrounds = {} 
        
        # Zoom of grid
        self.zoom = 1.0
        
        # Old curso position 
        self.old_cursor_row_col = 0, 0
    
    def get_textbox_edges(self, text_pos, text_extent):
        """Returns upper left, lower left, lower right, upper right of text"""
        
        string_x, string_y, angle = text_pos
        
        pt_ul =  string_x, string_y 
        pt_ll =  string_x, string_y + text_extent[1]
        pt_lr =  string_x + text_extent[0], string_y + text_extent[1]
        pt_ur =  string_x + text_extent[0], string_y
        
        if not -0.0001 < angle < 0.0001:
            rot_angle = angle / 180.0 * pi
            def rotation(x, y, angle, base_x=0.0, base_y=0.0):
                x -= base_x
                y -= base_y

                __x =  cos(rot_angle) * x + sin(rot_angle) * y
                __y = -sin(rot_angle) * x + cos(rot_angle) * y

                __x += base_x
                __y += base_y

                return __x, __y
            
            pt_ul = rotation(pt_ul[0], pt_ul[1], rot_angle, 
                              base_x=string_x, base_y=string_y)
            pt_ll = rotation(pt_ll[0], pt_ll[1], rot_angle, 
                              base_x=string_x, base_y=string_y)
            pt_ur = rotation(pt_ur[0], pt_ur[1], rot_angle, 
                              base_x=string_x, base_y=string_y)
            pt_lr = rotation(pt_lr[0], pt_lr[1], rot_angle, 
                              base_x=string_x, base_y=string_y)
        
        return pt_ul, pt_ll, pt_lr, pt_ur
    
    def get_text_rotorect(self, text_pos, text_extent):
        """Returns a RotoRect for given cell text"""
        
        import src.lib.xrect as xrect
        
        pt_ll = self.get_textbox_edges(text_pos, text_extent)[1]
        
        rr_x, rr_y = pt_ll
        
        angle = float(text_pos[2]) 
        
        return xrect.RotoRect(rr_x, rr_y, text_extent[0], text_extent[1], angle)
    
    def draw_textbox(self, dc, text_pos, text_extent):
    
        pt_ul, pt_ll, pt_lr, pt_ur = self.get_textbox_edges(text_pos, 
                                                            text_extent)
        
        dc.DrawLine(pt_ul[0], pt_ul[1], pt_ll[0], pt_ll[1])
        dc.DrawLine(pt_ll[0], pt_ll[1], pt_lr[0], pt_lr[1])
        dc.DrawLine(pt_lr[0], pt_lr[1], pt_ur[0], pt_ur[1])
        dc.DrawLine(pt_ur[0], pt_ur[1], pt_ul[0], pt_ul[1])

    def _get_full_cells(self, dc, grid, key, text_pos, text_extent):
        """Generator of full cells from key in direction
        
        Parameters
        ----------
        key: 3-tuple of Integer
        \tCurrent cell
        text_pos: 3-tuple
        \tPosition and direction of text

        """
        
        row, col, tab = key
        
        blocking_distance = None
        
        textbox = self.get_text_rotorect(text_pos, text_extent)
        
        for distance, __row, __col in grid.colliding_cells(row, col, textbox):
            # Draw blocking arrows if locking cell is not empty
            
            if not( \
               (blocking_distance is None or distance == blocking_distance) \
               and not self.data_array[__row, __col, tab]):
               
                yield __row, __col, tab

    def _get_empty_cells(self, dc, grid, key, text_pos, text_extent):
        """Generator of empty cells from key in direction
        
        Parameters
        ----------
        key: 3-tuple of Integer
        \tCurrent cell
        text_pos: 3-tuple
        \tPosition and direction of text

        """
        
        row, col, tab = key
        
        blocking_distance = None
        
        textbox = self.get_text_rotorect(text_pos, text_extent)
        
        for distance, __row, __col in grid.colliding_cells(row, col, textbox):
            
            if blocking_distance is None or distance == blocking_distance:
                if self.data_array[__row, __col, tab] is not None and \
                   self.data_array[__row, __col, tab] != "":
                    blocking_distance = distance
                else:
                    yield __row, __col, tab
    
    def _get_available_space_rects(self, dc, grid, key, rect, text_pos, 
                      text_extent, res_text):
        """Returns rects needed by key cell that are in available space"""
        
        yield rect
        
        for cell in self._get_empty_cells(dc, grid, key, text_pos, text_extent):
            __row, __col, _ = cell
            cell_rect = grid.CellToRect(__row, __col)
            
            yield cell_rect

    def draw_text_label(self, dc, res, rect, grid, key):
        """Draws text label of cell
        
        Text is truncated at config["max_result_length"]
        """
        
        result_length = config["max_result_length"]
        
        try:
            res_text = unicode(res)[:1000]
            
        except UnicodeDecodeError:
            res_text = unicode(res, encoding="utf-8")[:1000]
        
        
        if not res_text:
            return
        
        row, col, tab = key
        
        cell_attributes = self.data_array.cell_attributes[key]
        
        # Text font attributes
        textfont = cell_attributes["textfont"]
        pointsize = cell_attributes["pointsize"]
        fontweight = cell_attributes["fontweight"]
        fontstyle = cell_attributes["fontstyle"]
        underline = cell_attributes["underline"]
        
        strikethrough = cell_attributes["strikethrough"]
        
        # Text placement attributes
        vertical_align = cell_attributes["vertical_align"]
        justification = cell_attributes["justification"]
        angle = cell_attributes["angle"]
        
        # Text color attributes
        
        textcolor = wx.Color()
        textcolor.SetRGB(cell_attributes["textcolor"])
        
        # Get font from font attribute strings
        
        font = self.get_font(textfont, pointsize, fontweight, fontstyle, 
                             underline)
        
        dc.SetFont(font)
        
        text_x, text_y = self.get_text_position(dc, rect, res_text, angle,
                                                vertical_align, justification)
        
        __rect = xrect.Rect(rect.x, rect.y, rect.width, rect.height)
        
        text_extent = dc.GetTextExtent(res_text)
        
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetTextForeground(textcolor)
        
        # If cell rect stays inside cell, we simply draw
        
        text_pos = text_x, text_y, angle
        
        if all(__rect.is_point_in_rect(*textedge) \
          for textedge in self.get_textbox_edges(text_pos, text_extent)):
            clipping = False
        else:
            clipping = True
            clip_rects = self._get_available_space_rects(dc, grid, key, rect, 
                                text_pos, text_extent, res_text)
        
        if clipping:
            for clip_rect in clip_rects:
                dc.SetClippingRect(clip_rect)
                dc.DrawRotatedText(res_text, *text_pos)
                text_extent = dc.GetTextExtent(res_text)
                if strikethrough:
                    self._draw_strikethrough_line(grid, dc, rect, 
                            text_x, text_y, angle, text_extent)
                dc.DestroyClippingRegion()
        else:
            dc.DrawRotatedText(res_text, *text_pos)
            text_extent = dc.GetTextExtent(res_text)
            if strikethrough:
                self._draw_strikethrough_line(grid, dc, rect, 
                        text_x, text_y, angle, text_extent)
        
        
    def _draw_strikethrough_line(self, grid, dc, rect, 
                    string_x, string_y, angle, text_extent):
        """Draws a strikethrough line"""
            
        strikethroughwidth = max(1, int(round(1.5 * self.zoom)))
        dc.SetPen(wx.Pen(wx.BLACK, strikethroughwidth, wx.SOLID))

        x1 = string_x
        y1 = string_y + text_extent[1] / 2
        x2 = string_x + text_extent[0]
        y2 = string_y + text_extent[1] / 2

        if not -0.0001 < angle < 0.0001:

            rot_angle = angle / 180.0 * pi

            def rotation(x, y, angle, base_x=0.0, base_y=0.0):
                x -= base_x
                y -= base_y

                __x =  cos(rot_angle) * x + sin(rot_angle) * y
                __y = -sin(rot_angle) * x + cos(rot_angle) * y

                __x += base_x
                __y += base_y

                return __x, __y

            x1, y1 = rotation(x1, y1, rot_angle, 
                              base_x=string_x, base_y=string_y)
            x2, y2 = rotation(x2, y2, rot_angle,
                              base_x=string_x, base_y=string_y)

        dc.DrawLine(x1, y1, x2, y2)

    def get_font(self, textfont, pointsize, fontweight, fontstyle, underline):
        """Returns font for given attribute strings
        
        Parameters
        ----------
        
        textfont: String
        \tString that describes the type of font
        pointsize: Integer
        \tFont size in points
        fontweight: Integer in (wx.NORMAL, wx.BOLD)
        \tFontsize integer 
        fontstyle: Integer in (wx.NORMAL, wx.ITALICS)
        \tString that describes the font style
        underlined: Bool
        \tFont is underlined if True
        
        """
        
        # Get a real font from textfont string
        
        font = get_font_from_data(textfont)
        font.SetPointSize(self.get_zoomed_fontsize(pointsize))
        font.SetWeight(fontweight)
        font.SetStyle(fontstyle)
        font.SetUnderlined(underline)
        
        return font
    
    def get_zoomed_fontsize(self, font_size):
        """Returns zoomed font size as Integer
        
        Parameters
        ----------
        
        font_size: Integer
        \tOriginal font size
        
        """
        
        return max(1, int(round(font_size * self.zoom)))
    
    def get_text_position(self, dc, rect, res_text, angle, 
                          vertical_align, justification):
        """Returns text x, y position in cell"""
        
        text_extent = dc.GetTextExtent(res_text)
        
        # Vertical alignment
        
        if vertical_align == "middle":
            string_y = rect.y + rect.height / 2 - text_extent[1] / 2 + 1
            
        elif vertical_align == "bottom":
            string_y = rect.y + rect.height - text_extent[1]
        
        elif vertical_align == "top":
            string_y = rect.y + 2
            
        else:
            raise ValueError, "Vertical alignment " + vertical_align + \
                              "not in (top, middle, bottom)"
        
        # Justification
        
        if justification == "left":
            string_x = rect.x + 2
            
        elif justification == "center":
            # First calculate x value for unrotated text
            string_x = rect.x + rect.width / 2 - 1
            
            # Now map onto rotated xy position
            rot_angle = angle / 180.0 * pi
            string_x = string_x - text_extent[0] / 2 * cos(rot_angle)
            string_y = string_y + text_extent[0] / 2 * sin(rot_angle)

        elif justification == "right":
            # First calculate x value for unrotated text
            string_x = rect.x + rect.width - 2
            
            # Now map onto rotated xy position
            rot_angle = angle / 180.0 * pi
            string_x = string_x - text_extent[0] * cos(rot_angle)
            string_y = string_y + text_extent[0] * sin(rot_angle)
        else:
            raise ValueError, "Cell justification " + justification + \
                              "not in (left, center, right)"
    
        return string_x, string_y
        

    def _draw_cursor(self, dc, grid, row, col, 
                    pen=wx.BLACK_PEN, brush=wx.BLACK_BRUSH):
        """Draws cursor as Reckangle in lower right corner"""
        
        rect = grid.CellToRect(row, col)
        
        size = max(1, int(self.zoom))
        
        caret_length = int(min([rect.width, rect.height]) / 5.0)
        
        pen.SetWidth(size)
        
        # Inner right and lower borders
        border_left = rect.x
        border_right = rect.x + rect.width - size - 1
        border_upper = rect.y
        border_lower = rect.y + rect.height - size - 1
        
        points_lr = [ \
            (border_right, border_lower - caret_length),
            (border_right, border_lower),
            (border_right - caret_length, border_lower),
            (border_right, border_lower),
        ]
        
        points_ur = [ \
            (border_right, border_upper + caret_length),
            (border_right, border_upper),
            (border_right - caret_length, border_upper),
            (border_right, border_upper),
        ]
        
        points_ul = [ \
            (border_left, border_upper + caret_length),
            (border_left, border_upper),
            (border_left + caret_length, border_upper),
            (border_left, border_upper),
        ]
        
        points_ll = [ \
            (border_left, border_lower - caret_length),
            (border_left, border_lower),
            (border_left + caret_length, border_lower),
            (border_left, border_lower),
        ]
        
        point_list = [points_lr, points_ur, points_ul, points_ll]
        
        dc.DrawPolygonList(point_list, pens=pen, brushes=brush)
        
        self.old_cursor_row_col = row, col
    
    def update_cursor(self, dc, grid, row, col):
        """Whites out the old cursor and draws the new one"""
        
        ## TODO: Use background color for deletion
        old_row, old_col = self.old_cursor_row_col
        
        self._draw_cursor(dc, grid, old_row, old_col, 
                         pen=wx.WHITE_PEN, brush=wx.WHITE_BRUSH)
        self._draw_cursor(dc, grid, row, col)
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected, printing=False):
        """Draws the cell border and content"""
        
        key = (row, col, grid.current_table)
        
        if isSelected:
            grid.selection_present = True
            
            bg = Background(grid, self.data_array, row, col, grid.current_table,
                            isSelected)
        else:
            _, _, width, height = grid.CellToRect(row, col)
            
            bg_components = ["bgcolor", 
                             "borderwidth_bottom", "borderwidth_right", 
                             "bordercolor_bottom", "bordercolor_right"]
            
            bg_key = tuple([width, height] + \
                           [self.data_array.cell_attributes[key][bgc] \
                                            for bgc in bg_components])
            
            try:
                bg = self.backgrounds[bg_key]
                
            except KeyError:
                if len(self.backgrounds) > 10000:
                    # self.backgrounds may grow quickly
                    
                    self.backgrounds = {}
                
                bg = self.backgrounds[bg_key] = \
                        Background(grid, self.data_array, *key)
            
        if wx.Platform == "__WXGTK__" and not printing:
            mask_type = wx.AND
        else:
            mask_type = wx.COPY
            
        dc.Blit(rect.x, rect.y, rect.width, rect.height,
                bg.dc, 0, 0, mask_type)
        
        
        # Check if the dc is drawn manually be a return func
        
        res = self.data_array[row, col, grid.current_table]
        
        if type(res) is types.FunctionType:
            # Add func_dict attribute 
            # so that we are sure that it uses a dc
            try:
                res(grid, attr, dc, rect)
            except TypeError:
                pass
        
        elif res is not None:
            self.draw_text_label(dc, res, rect, grid, key)
        
        if grid.actions.cursor[:2] == (row, col):
            self.update_cursor(dc, grid, row, col)
        
# end of class TextRenderer


class Background(object):
    """Memory DC with background content for given cell"""
    
    def __init__(self, grid, data_array, row, col, tab, selection=False):
        self.grid = grid
        self.data_array = data_array
        
        self.key = row, col, tab
        
        self.dc = wx.MemoryDC() 
        self.rect = grid.CellToRect(row, col)
        self.bmp = wx.EmptyBitmap(self.rect.width,self.rect.height)
        
        self.selection = selection
        
        self.dc.SelectObject(self.bmp)
        self.dc.SetBackgroundMode(wx.TRANSPARENT)

        self.dc.SetDeviceOrigin(0,0)
        
        self.draw()
        
    def draw(self):
        """Does the actual background drawing"""
        
        self.draw_background(self.dc)
        self.draw_border_lines(self.dc)

    def draw_background(self, dc):
        """Draws the background of the background"""
        
        color = wx.Colour()
        
        if self.selection:
            color.Set(*config["selection_color"])
        else:
            rgb = self.data_array.cell_attributes[self.key]["bgcolor"]
            color.SetRGB(rgb)
        
        bgbrush = wx.Brush(color, wx.SOLID)
        
        dc.SetBrush(bgbrush)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(0, 0, self.rect.width, self.rect.height)

    def draw_border_lines(self, dc):
        """Draws lines"""
        
        x, y, w, h  = 0, 0, self.rect.width - 1, self.rect.height - 1
        grid = self.grid
        row, col, tab = key = self.key
        
        # Get borderpens and bgbrushes for rects        
        # Each cell draws its bottom and its right line only
        bottomline = x, y + h, x + w, y + h
        rightline = x + w, y, x + w, y + h
        lines = [bottomline, rightline]
        
        # Bottom line pen
        
        color = self.data_array.cell_attributes[key]["bordercolor_bottom"]
        width = self.data_array.cell_attributes[key]["borderwidth_bottom"]
        bottom_pen = get_pen_from_data((color, width, int(wx.SOLID)))
        
        # Right line pen
        
        color = self.data_array.cell_attributes[key]["bordercolor_right"]
        width = self.data_array.cell_attributes[key]["borderwidth_right"]
        right_pen = get_pen_from_data((color, width, int(wx.SOLID)))
        
        borderpens = bottom_pen, right_pen
        
#        # Topmost line if in top cell
#        
#        if row == 0:
#            lines.append((x, y, x + w, y))
#            topkey = "top", col, tab
#            toppen_data = self.data_array.cell_attributes[topkey][pen_names[0]]
#            borderpens.append(get_pen_from_data(toppen_data))
#        
#        # Leftmost line if in left cell
#        
#        if col == 0:
#            lines.append((x, y, x, y + h))
#            leftkey = row, "left", tab
#            toppen_data  = self.data_array.cell_attributes[leftkey][pen_names[1]]
#            borderpens.append(get_pen_from_data(toppen_data))
        
        zoomed_pens = []
        
        for pen in borderpens:
            bordercolor = pen.GetColour()
            borderwidth = pen.GetWidth()
            borderstyle = pen.GetStyle()
            
            zoomed_borderwidth = max(1, 
                int(round(borderwidth * self.grid.grid_renderer.zoom)))
            zoomed_pen = wx.Pen(bordercolor, zoomed_borderwidth, borderstyle)
            zoomed_pen.SetJoin(wx.JOIN_MITER)
            
            zoomed_pens.append(zoomed_pen)
        
        dc.DrawLineList(lines, zoomed_pens)

# end of class Background

