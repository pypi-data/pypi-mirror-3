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

from distutils.core import setup

setup(name='pyspread',
      version='0.2.2',
      description='Python Spreadsheet',
      license='GPL v3 :: GNU General Public License',
      keywords=['spreadsheet', 'pyspread'],
      author='Martin Manns',
      author_email='mmanns@gmx.net',
      url='http://manns.github.com/pyspread/',
      requires=['numpy (>=1.1)', 'wx (>=2.8.10)', 'pyme (>=0.8)'],
      packages=[''],
      scripts=['pyspread/pyspread'],
      package_data={'':
        ['pyspread/*.py',
         'pyspread/src/*.py',
         'pyspread/src/pyspread',
         'pyspread/src/*/*.py',
         'pyspread/src/*/test/*.py',
         'pyspread/src/*/test/*.pys*',
         'pyspread/src/*/test/*.sig',
         'pyspread/src/*/test/*.csv',
         'pyspread/src/*/test/*.txt',
         'pyspread/src/*/test/*.pys*',
         'pyspread/share/icons/*.png',
         'pyspread/share/icons/Tango/24x24/actions/*.png',
         'pyspread/share/icons/Tango/24x24/toggles/*.png',
         'pyspread/share/icons/Tango/24x24/toggles/*.xpm',
         'pyspread/doc/help/*.html',
         'pyspread/doc/help/images/*.png',
         'pyspread/po/*',
         'pyspread/examples/*',
         'pyspread/COPYING', 'pyspread/thanks', 'pyspread/faq',
         'pyspread/authors', 'pyspread.pth', 'README', 'changelog']},
      classifiers=[ \
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
      ],
)