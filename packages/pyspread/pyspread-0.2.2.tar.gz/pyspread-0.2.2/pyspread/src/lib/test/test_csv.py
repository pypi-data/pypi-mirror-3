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
test_csv
========

Unit tests for __csv.py

"""


import wx
app = wx.App()

import src.lib.__csv as __csv

def test_sniff():
    """Unit test for sniff"""

    pass
#    dialect, header = __csv.sniff("BUG2037662.csv")
#    assert not header
#    assert dialect.delimiter == ','
#    assert dialect.doublequote == 0
#    assert dialect.quoting == 0
#    assert dialect.quotechar == '"'
#    assert dialect.lineterminator == "\r\n"
#    assert dialect.skipinitialspace == 0

def test_get_first_line():
    """Unit test for get_first_line"""

    pass

def test_csv_digest_gen():
    """Unit test for csv_digest_gen"""

    pass

def test_cell_key_val_gen():
    """Unit test for cell_key_val_gen"""

    pass


class TestDigest(object):
    """Unit tests for Digest"""

    def test_make_string(self):
        """Unit test for make_string"""

        pass

    def test_make_unicode(self):
        """Unit test for make_unicode"""

        pass

    def test_make_slice(self):
        """Unit test for make_slice"""

        pass

    def test_make_date(self):
        """Unit test for make_date"""

        pass

    def test_make_datetime(self):
        """Unit test for make_datetime"""

        pass

    def test_make_time(self):
        """Unit test for make_time"""

        pass

    def test_make_object(self):
        """Unit test for make_object"""

        pass

    def test_call(self):
        """Unit test for __call__"""

        pass


class TestCsvInterface(object):
    """Unit tests for CsvInterface"""

    def test_iter(self):
        """Unit test for __iter__"""

        pass

    def test_get_csv_cells_gen(self):
        """Unit test for _get_csv_cells_gen"""

        pass

    def test_write(self):
        """Unit test for write"""

        pass

class TestTxtGenerator(object):
    """Unit tests for TxtGenerator"""

    def test_iter(self):
        """Unit test for __iter__"""

        pass

