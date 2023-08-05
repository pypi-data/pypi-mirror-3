#!/usr/bin/env python

from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(name='pyspread',
      version='0.2.0',
      description='Python Spreadsheet',
      license='GPL v3 :: GNU General Public License',
      keywords=['spreadsheet', 'pyspread'],
      author='Martin Manns',
      author_email='mmanns@gmx.net',
      url='http://manns.github.com/pyspread/',
      requires=['numpy (>=1.1)', 'wx (>=2.8.10)'],
      packages=[''],
      scripts=['pyspread/pyspread'],
      package_data={'':
        ['pyspread/*.py',
         'pyspread/src/*.py',
         'pyspread/src/pyspread',
         'pyspread/src/*/*.py',
         'pyspread/src/*/test/*',
         'pyspread/share/icons/*.png',
         'pyspread/share/icons/Tango/24x24/actions/*.png', 
         'pyspread/share/icons/Tango/24x24/toggles/*.png', 
         'pyspread/share/icons/Tango/24x24/toggles/*.xpm',
         'pyspread/doc/help/*.html', 
         'pyspread/doc/help/images/*.png',
         'pyspread/examples/*',
         'pyspread/COPYING', 'pyspread/thanks', 'pyspread/faq', 
         'authors', 'pyspread.pth']},
      classifiers=[ \
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
      ],
)
