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
run_tests
=========

Runs all unit tests for pyspread

"""

import os

from sysvars import get_program_path

import wx
app = wx.App()

from src.lib.gpg import genkey, sign


# Remember to set PYTHONPATH to current dir


def create_valid_signatures():
    """Createsb all valid signatures for test files"""

    source_path = get_program_path() + "src/"

    valid_test_filepaths = [ \
        source_path + "actions/test/test1.pys",
        source_path + "actions/test/test4.pys",
        source_path + "lib/test/test1.pys",
    ]

    for filepath in valid_test_filepaths:
        try:
            os.remove(filepath + ".sig")
        except OSError:
            pass

        signature = sign(filepath)
        signfile = open(filepath + '.sig', 'wb')
        signfile.write(signature)
        signfile.close()


def run_tests():
    """Looks for py.test files and runs py.test"""

    source_path = get_program_path() + "src/"

    for root, dirs, files in os.walk(source_path):
        if root[-4:] == "test":
            for __file in files:
                if __file[:4] == "test" and __file[-2:] == "py":
                    # We have a test file
                    cd_op = "cd " + root
                    test_op = "py.test " + __file
                    sys_cmd = cd_op + " && " + test_op
                    os.system(sys_cmd)

if __name__ == "__main__":

    genkey()

    create_valid_signatures()

    run_tests()