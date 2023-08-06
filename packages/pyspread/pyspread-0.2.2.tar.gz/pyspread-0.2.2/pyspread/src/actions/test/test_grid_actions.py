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
test_grid_actions
=================

Unit tests for _grid_actions.py

"""

import os

import bz2
import wx
app = wx.App()

from src.lib.selection import Selection

from src.lib.testlib import main_window, grid, code_array
from src.lib.testlib import params, pytest_generate_tests
from src.lib.testlib import basic_setup_test, restore_basic_grid

from src.lib.gpg import sign

from src.gui._events import *

class TestFileActions(object):
    """File actions test class"""

    def setup_method(self, method):

        # Filenames
        # ---------

        # File with valid signature
        self.filename_valid_sig = "test1.pys"
        sign(self.filename_valid_sig)

        # File without signature
        self.filename_no_sig = "test2.pys"

        # File with invalid signature
        self.filename_invalid_sig = "test3.pys"

        # File for grid size test
        self.filename_gridsize = "test4.pys"
        sign(self.filename_gridsize)

        # Empty file
        self.filename_empty = "test5.pys"

        # File name that cannot be accessed
        self.filename_not_permitted = "test6.pys"

        # File name without file
        self.filename_wrong = "test-1.pys"

        # File for testing save
        self.filename_save = "test_save.pys"

    def test_validate_signature(self):
        """Tests signature validation"""

        # Test missing sig file
        assert not grid.actions.validate_signature(self.filename_no_sig)

        # Test valid sig file
        assert grid.actions.validate_signature(self.filename_valid_sig)

        # Test invalid sig file
        assert not \
            grid.actions.validate_signature(self.filename_invalid_sig)

    def test_enter_safe_mode(self):
        """Tests safe mode entry"""

        grid.actions.leave_safe_mode()
        grid.actions.enter_safe_mode()
        assert grid.code_array.safe_mode

    def test_leave_safe_mode(self):
        """Tests save mode exit"""

        grid.actions.enter_safe_mode()
        grid.actions.leave_safe_mode()
        assert not grid.code_array.safe_mode

    def test_approve(self):

        # Test if safe_mode is correctly set for invalid sig
        grid.actions.approve(self.filename_invalid_sig)

        assert grid.GetTable().data_array.safe_mode

        # Test if safe_mode is correctly set for valid sig

        grid.actions.approve(self.filename_valid_sig)

        assert not grid.GetTable().data_array.safe_mode

        # Test if safe_mode is correctly set for missing sig
        grid.actions.approve(self.filename_no_sig)

        assert grid.GetTable().data_array.safe_mode

        # Test if safe_mode is correctly set for io-error sig

        os.chmod(self.filename_not_permitted, 0200)
        os.chmod(self.filename_not_permitted + ".sig", 0200)

        grid.actions.approve(self.filename_not_permitted)

        assert grid.GetTable().data_array.safe_mode

        os.chmod(self.filename_not_permitted, 0644)
        os.chmod(self.filename_not_permitted + ".sig", 0644)

    def test_get_file_version(self):
        """Tests infile version string."""

        infile = bz2.BZ2File(self.filename_valid_sig)
        version = grid.actions._get_file_version(infile)
        assert version == "0.1"
        infile.close()

    def test_clear(self):
        """Tests empty_grid method"""

        # Set up grid

        grid.code_array[(0, 0, 0)] = "'Test1'"
        grid.code_array[(3, 1, 1)] = "'Test2'"

        grid.actions.set_col_width(1, 23)
        grid.actions.set_col_width(0, 233)
        grid.actions.set_row_height(0, 0)

        selection = Selection([],[],[],[],[(0, 0)])
        grid.actions.set_attr("bgcolor", wx.RED, selection)
        grid.actions.set_attr("frozen", "print 'Testcode'", selection)

        # Clear grid

        grid.actions.clear()

        # Code content

        assert grid.code_array((0, 0, 0)) is None
        assert grid.code_array((3, 1, 1)) is None

        assert list(grid.code_array[:2, 0, 0]) == [None, None]

        # Cell attributes
        cell_attributes = grid.code_array.cell_attributes
        assert cell_attributes == []

        # Row heights and column widths

        row_heights = grid.code_array.row_heights
        assert len(row_heights) == 0

        col_widths = grid.code_array.col_widths
        assert len(col_widths) == 0

        # Undo and redo
        undolist = grid.code_array.unredo.undolist
        redolist = grid.code_array.unredo.redolist
        assert undolist == []
        assert redolist == []

        # Caches

        # Clear grid again because lookup is added in resultcache

        grid.actions.clear()

        result_cache = grid.code_array.result_cache
        assert len(result_cache) == 0

    def test_open(self):
        """Tests open functionality"""

        class Event(object):
            attr = {}
        event = Event()

        # Test missing file
        event.attr["filepath"] = self.filename_wrong

        assert not grid.actions.open(event)

        # Test unaccessible file
        os.chmod(self.filename_not_permitted, 0200)
        event.attr["filepath"] = self.filename_not_permitted
        assert not grid.actions.open(event)

        os.chmod(self.filename_not_permitted, 0644)

        # Test empty file
        event.attr["filepath"] = self.filename_empty
        assert not grid.actions.open(event)

        assert grid.GetTable().data_array.safe_mode # sig is also empty

        # Test invalid sig files
        event.attr["filepath"] = self.filename_invalid_sig
        grid.actions.open(event)

        assert grid.GetTable().data_array.safe_mode

        # Test file with sig
        event.attr["filepath"] = self.filename_valid_sig
        grid.actions.open(event)

        assert not grid.GetTable().data_array.safe_mode

        # Test file without sig
        event.attr["filepath"] = self.filename_no_sig
        grid.actions.open(event)

        assert grid.GetTable().data_array.safe_mode

        # Test grid size for valid file
        event.attr["filepath"] = self.filename_gridsize
        grid.actions.open(event)

        new_shape = grid.GetTable().data_array.shape
        assert new_shape == (1000, 100, 10)

        # Test grid content for valid file

        assert grid.GetTable().data_array[0, 0, 0] == "test4"

    def test_save(self):
        """Tests save functionality"""

        class Event(object):
            attr = {}
        event = Event()

        # Test normal save
        event.attr["filepath"] = self.filename_save

        grid.actions.save(event)

        savefile = open(self.filename_save)

        assert savefile
        savefile.close()

        # Test double filename

        grid.actions.save(event)

        # Test io error

        os.chmod(self.filename_save, 0200)
        try:
            grid.actions.save(event)
            raise IOError, "No error raised even though target not writable"
        except IOError:
            pass
        os.chmod(self.filename_save, 0644)

        # Test invalid file name

        event.attr["filepath"] = None
        try:
            grid.actions.save(event)
            raise TypeError, "None accepted as filename"
        except TypeError:
            pass

        # Test sig creation is happening

        sigfile = open(self.filename_save + ".sig")
        assert sigfile
        sigfile.close()

        os.remove(self.filename_save)
        os.remove(self.filename_save + ".sig")

    def test_sign_file(self):
        """Tests signing functionality"""

        os.remove(self.filename_valid_sig + ".sig")
        grid.actions.sign_file(self.filename_valid_sig)
        dirlist = os.listdir(".")
        assert self.filename_valid_sig + ".sig" in dirlist

class TestTableRowActionsMixins(object):
    """Unit test class for TableRowActionsMixins"""

    param_set_row_height = [ \
        {'row': 0, 'tab': 0, 'height': 0},
        {'row': 0, 'tab': 1, 'height': 0},
        {'row': 0, 'tab': 0, 'height': 34},
        {'row': 10, 'tab': 12, 'height': 3245.78},
    ]

    @params(param_set_row_height)
    def test_set_row_height(self, row, tab, height):
        grid.current_table = tab
        grid.actions.set_row_height(row, height)
        row_heights = grid.code_array.row_heights
        assert row_heights[row, tab] == height

    param_insert_rows = [ \
        {'row': 0, 'no_rows': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'row': 0, 'no_rows': 1, 'test_key': (0, 0, 0), 'test_val': None},
        {'row': 0, 'no_rows': 1, 'test_key': (1, 0, 0), 'test_val': "'Test'"},
        {'row': 0, 'no_rows': 5, 'test_key': (5, 0, 0), 'test_val': "'Test'"},
        {'row': 1, 'no_rows': 1, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'row': 1, 'no_rows': 1, 'test_key': (1, 0, 0), 'test_val': None},
        {'row': 1, 'no_rows': 1, 'test_key': (2, 1, 0), 'test_val': "3"},
        {'row': 1, 'no_rows': 5000, 'test_key': (5001, 1, 0), 'test_val': "3"},
    ]

    @params(param_insert_rows)
    def test_insert_rows(self, row, no_rows, test_key, test_val):
        """Tests insertion action for rows"""

        basic_setup_test(grid.actions.insert_rows, test_key, test_val,
                         row, no_rows=no_rows)

    param_delete_rows = [ \
       {'row': 0, 'no_rows': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
       {'row': 0, 'no_rows': 1, 'test_key': (0, 0, 0), 'test_val': None},
       {'row': 0, 'no_rows': 1, 'test_key': (0, 1, 0), 'test_val': "3"},
       {'row': 0, 'no_rows': 995, 'test_key': (4, 99, 0), 'test_val': "$^%&$^"},
       {'row': 1, 'no_rows': 1, 'test_key': (0, 1, 0), 'test_val': "1"},
       {'row': 1, 'no_rows': 1, 'test_key': (1, 1, 0), 'test_val': None},
       {'row': 1, 'no_rows': 999, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
    ]

    @params(param_delete_rows)
    def test_delete_rows(self, row, no_rows, test_key, test_val):
        """Tests deletion action for rows"""

        basic_setup_test(grid.actions.delete_rows, test_key, test_val,
                         row, no_rows=no_rows)


class TestTableColumnActionsMixin(object):
    """Unit test class for TableColumnActionsMixin"""

    param_set_col_width = [ \
        {'col': 0, 'tab': 0, 'width': 0},
        {'col': 0, 'tab': 1, 'width': 0},
        {'col': 0, 'tab': 0, 'width': 34},
        {'col': 10, 'tab': 12, 'width': 3245.78},
    ]

    @params(param_set_col_width)
    def test_set_col_width(self, col, tab, width):
        grid.current_table = tab
        grid.actions.set_col_width(col, width)
        col_widths = grid.code_array.col_widths
        assert col_widths[col, tab] == width

    param_insert_cols = [ \
        {'col': 0, 'no_cols': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'col': 0, 'no_cols': 1, 'test_key': (0, 0, 0), 'test_val': None},
        {'col': 0, 'no_cols': 1, 'test_key': (0, 1, 0), 'test_val': "'Test'"},
        {'col': 0, 'no_cols': 5, 'test_key': (0, 5, 0), 'test_val': "'Test'"},
        {'col': 1, 'no_cols': 1, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'col': 1, 'no_cols': 1, 'test_key': (0, 1, 0), 'test_val': None},
        {'col': 1, 'no_cols': 1, 'test_key': (1, 2, 0), 'test_val': "3"},
        {'col': 1, 'no_cols': 5000, 'test_key': (1, 5001, 0), 'test_val': "3"},
    ]

    @params(param_insert_cols)
    def test_insert_cols(self, col, no_cols, test_key, test_val):
        """Tests insertion action for columns"""

        basic_setup_test(grid.actions.insert_cols, test_key, test_val,
                         col, no_cols=no_cols)


    param_delete_cols = [ \
       {'col': 0, 'no_cols': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
       {'col': 0, 'no_cols': 1, 'test_key': (0, 2, 0), 'test_val': None},
       {'col': 0, 'no_cols': 1, 'test_key': (0, 1, 0), 'test_val': "2"},
       {'col': 0, 'no_cols': 95, 'test_key': (999, 4, 0), 'test_val': "$^%&$^"},
       {'col': 1, 'no_cols': 1, 'test_key': (0, 1, 0), 'test_val': "2"},
       {'col': 1, 'no_cols': 1, 'test_key': (1, 1, 0), 'test_val': "4"},
       {'col': 1, 'no_cols': 99, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
    ]

    @params(param_delete_cols)
    def test_delete_cols(self, col, no_cols, test_key, test_val):
        """Tests deletion action for columns"""

        basic_setup_test(grid.actions.delete_cols, test_key, test_val,
                         col, no_cols=no_cols)


class TestTableTabActionsMixin(object):
    """Unit test class for TableTabActionsMixin"""

    param_insert_tabs = [ \
        {'tab': 0, 'no_tabs': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'tab': 0, 'no_tabs': 1, 'test_key': (0, 0, 0), 'test_val': None},
        {'tab': 0, 'no_tabs': 1, 'test_key': (0, 0, 1), 'test_val': "'Test'"},
        {'tab': 0, 'no_tabs': 5, 'test_key': (0, 0, 5), 'test_val': "'Test'"},
        {'tab': 1, 'no_tabs': 1, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
        {'tab': 1, 'no_tabs': 1, 'test_key': (0, 0, 1), 'test_val': None},
        {'tab': 1, 'no_tabs': 1, 'test_key': (1, 2, 3), 'test_val': "78"},
        {'tab': 1, 'no_tabs': 5000, 'test_key': (1, 2, 5002), 'test_val': "78"},
    ]

    @params(param_insert_tabs)
    def test_insert_tabs(self, tab, no_tabs, test_key, test_val):
        """Tests insertion action for tabs"""

        basic_setup_test(grid.actions.insert_tabs, test_key, test_val,
                         tab, no_tabs=no_tabs)

    param_delete_tabs = [ \
       {'tab': 0, 'no_tabs': 0, 'test_key': (0, 0, 0), 'test_val': "'Test'"},
       {'tab': 0, 'no_tabs': 1, 'test_key': (0, 2, 0), 'test_val': None},
       {'tab': 0, 'no_tabs': 1, 'test_key': (1, 2, 1), 'test_val': "78"},
       {'tab': 2, 'no_tabs': 1, 'test_key': (1, 2, 1), 'test_val': None},
       {'tab': 1, 'no_tabs': 1, 'test_key': (1, 2, 1), 'test_val': "78"},
       {'tab': 0, 'no_tabs': 2, 'test_key': (1, 2, 0), 'test_val': "78"},
    ]

    @params(param_delete_tabs)
    def test_delete_tabs(self, tab, no_tabs, test_key, test_val):
        """Tests deletion action for tabs"""

        basic_setup_test(grid.actions.delete_tabs, test_key, test_val,
                         tab, no_tabs=no_tabs)

class TestTableActions(object):
    """Unit test class for TableActions"""

    param_paste = [ \
       {'tl_cell': (0, 0, 0), 'data': [["78"]],
        'test_key': (0, 0, 0), 'test_val': "78"},
       {'tl_cell': (0, 0, 0), 'data': [[None]],
        'test_key': (0, 0, 0), 'test_val': None},
       {'tl_cell': (0, 0, 0), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (0, 0, 0), 'test_val': "1"},
       {'tl_cell': (0, 0, 0), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (1, 1, 0), 'test_val': "4"},
       {'tl_cell': (0, 0, 0), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (1, 1, 1), 'test_val': None},
       {'tl_cell': (1, 0, 0), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (0, 0, 0), 'test_val': "'Test'"},
       {'tl_cell': (1, 0, 0), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (1, 0, 0), 'test_val': "1"},
       {'tl_cell': (0, 1, 0), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (0, 1, 0), 'test_val': "1"},
       {'tl_cell': (0, 1, 0), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (0, 0, 0), 'test_val': "'Test'"},
       {'tl_cell': (123, 5, 0), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (123, 6, 0), 'test_val': "2"},
       {'tl_cell': (1, 1, 2), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (1, 1, 2), 'test_val': "1"},
       {'tl_cell': (1, 1, 2), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (1, 1, 0), 'test_val': "3"},
       {'tl_cell': (999, 0, 0), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (999, 0, 0), 'test_val': "1"},
       {'tl_cell': (999, 99, 2), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (999, 99, 2), 'test_val': "1"},
       {'tl_cell': (999, 98, 2), 'data': [["1", "2"], ["3", "4"]],
        'test_key': (999, 99, 2), 'test_val': "2"},
    ]

    @params(param_paste)
    def test_paste(self, tl_cell, data, test_key, test_val):
        """Tests paste into grid"""

        basic_setup_test(grid.actions.paste, test_key, test_val, tl_cell, data)

    param_change_grid_shape = [ \
       {'shape': (1, 1, 1)},
       {'shape': (2, 1, 3)},
       {'shape': (1, 1, 40)},
       {'shape': (1000, 100, 3)},
       {'shape': (80000000, 80000000, 80000000)},
    ]

    @params(param_change_grid_shape)
    def test_change_grid_shape(self, shape):
        """Tests action for changing the grid shape"""

        grid.actions.clear()

        grid.actions.change_grid_shape(shape)

        res_shape = grid.code_array.shape
        assert res_shape == shape

        br_key = tuple(dim - 1 for dim in shape)
        assert grid.code_array(br_key) is None


class TestUnRedoActions(object):
    """Unit test class for undo and redo actions"""

    def test_undo(self):
        """Tests undo action"""

        restore_basic_grid()
        grid.actions.clear()

        grid.code_array[(0, 0, 0)] = "Test"

        grid.actions.undo()

        assert grid.code_array((0, 0, 0)) is None

    def test_redo(self):
        """Tests redo action"""

        self.test_undo()
        grid.actions.redo()

        assert grid.code_array((0, 0, 0)) == "Test"


class TestGridActions(object):
    """Grid level grid actions test class"""

    class Event(object):
        pass

    def test_new(self):
        """Tests creation of a new spreadsheets"""

        dims = [1, 1, 1, 10, 1, 1, 1, 10, 1, 1, 1, 10, 10, 10, 10]
        dims = zip(dims[::3], dims[1::3], dims[2::3])

        for dim in dims:
            event = self.Event()
            event.shape = dim
            grid.actions.new(event)
            new_shape = grid.GetTable().data_array.shape
            assert new_shape == dim

    param_switch_to_table = [ \
       {'tab': 2},
       {'tab': 0},
    ]

    @params(param_switch_to_table)
    def test_switch_to_table(self, tab):
        event = self.Event()
        event.newtable = tab
        grid.actions.switch_to_table(event)
        assert grid.current_table == tab

    param_cursor = [ \
       {'key': (0, 0, 0)},
       {'key': (0, 1, 2)},
       {'key': (999, 99, 1)},
    ]

    @params(param_cursor)
    def test_cursor(self, key):
        grid.cursor = key
        assert grid.cursor == key


class TestSelectionActions(object):
    """Selection actions test class"""

    # No tests yet because of close integration with selection in GUI

    pass


class TestFindActions(object):
    """FindActions test class"""

    # No tests yet because of close integration with selection in GUI

    pass
