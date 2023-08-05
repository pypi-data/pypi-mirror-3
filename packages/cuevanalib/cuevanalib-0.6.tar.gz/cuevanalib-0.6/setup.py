#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup

import sys

from cuevanalib import __version__

if sys.version_info < (2, 6):
    print('ERROR: cuevanalib requires at least Python 2.6 to run.')
    sys.exit(1)

long_description = open('README.rst').read()

dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
                'tk84.dll']
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']

setup(
    name = 'cuevanalib',
    version = __version__,
    description = 'A lib trying to work as cuevana.tv missing API',
    long_description = long_description,
    author = u'Martín Gaitán'.encode("UTF-8"),
    author_email = 'gaitan@gmail.com',
    url='https://bitbucket.org/tin_nqn/cuevanalib',
    packages = ['cuevanalib', ],
    license = 'GNU GENERAL PUBLIC LICENCE v3.0 (see LICENCE.txt)',
    install_requires = ['pyquery>=0.5', 'progressbar'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],

)
