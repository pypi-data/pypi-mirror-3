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
test_gpg
========

Unit tests for gpg.py

"""

from sys import path, modules

path.insert(0, "..") 
path.insert(0, "../..") 

import wx
app = wx.App()

import os

import lib.gpg as gpg
from src.lib.testlib import params, pytest_generate_tests

from src.config import config
    
def test_is_pyme_present():
    """Unit test for is_pyme_present"""
    
    try:
        import pyme
        pyme_present = True
    except ImportError:
        pyme_present = False
        
    assert gpg.is_pyme_present() == pyme_present

def _set_sig(filename, sigfilename):
    
    
    signature = gpg.sign(filename)
    
    sigfile = open(sigfilename, "w")
    sigfile.write(signature)
    sigfile.close()

def test_sign():
    """Unit test for sign"""
    
    filename = "test1.pys"
    sigfilename = filename + ".sig"
    
    _set_sig(filename, sigfilename)
    
    valid = gpg.verify(sigfilename, filename)
    
    assert valid

param_verify = [ \
    {'filename': "test1.pys", 'sigfilename': "test1.pys.sig", 'valid': True},
    {'filename': "test1.pys", 'sigfilename': "test1.pys.empty", 'valid': False},
    {'filename': "test1.pys", 'sigfilename': "test1.pys.nonsense", 
     'valid': False},
]

@params(param_verify)
def test_sign_verify(filename, sigfilename, valid):
    """Unit test for verify"""
    
    assert valid == gpg.verify(sigfilename, filename)    
    
