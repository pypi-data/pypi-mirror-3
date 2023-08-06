#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 Martin Manns
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
i18n
====

This module handles internationalization

"""

import os
import locale
import gettext
import sys

#  Translation files are located in
#  @LOCALE_DIR@/@LANGUAGE@/LC_MESSAGES/@APP_NAME@.mo
APP_NAME = "pyspread"

APP_DIR = os.path.join(sys.prefix, 'share')

# .mo files  are located in APP_Dir/i18n/LANGUAGECODE/LC_MESSAGES/
LOCALE_DIR = os.path.join(APP_DIR, 'i18n')


# Choose the language
# -------------------
# A list is provided,gettext uses the first translation available in the list
DEFAULT_LANGUAGES = os.environ.get('LANGUAGES', '').split(':')
DEFAULT_LANGUAGES += ['en_US']

lc, encoding = locale.getdefaultlocale()
if lc:
    languages = [lc]

# Languages and locations of translations are in env + default locale

languages += DEFAULT_LANGUAGES
mo_location = LOCALE_DIR

# gettext initialization
# ----------------------

gettext.install(True, localedir=None, unicode=1)

gettext.find(APP_NAME, mo_location)

gettext.textdomain(APP_NAME)

gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")

language = gettext.translation(APP_NAME, mo_location, languages=languages,
                               fallback=True)