#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup

import sys
try:
    import py2exe
except:
    #no windows platform
    pass

from cuevanalinks import __version__

if sys.version_info < (2, 6):
    print('ERROR: cuevanalinks requires at least Python 2.6 to run.')
    sys.exit(1)

long_description = open('README.rst').read()

dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
                'tk84.dll']
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']

setup(
    name = 'CuevanaLinks',
    version = __version__,
    description = 'A program to retrieve movies and series (or its links)\
                    from cuevana.tv',
    long_description = long_description,
    author = u'Martín Gaitán'.encode("UTF-8"),
    author_email = 'gaitan@gmail.com',
    url='https://bitbucket.org/tin_nqn/cuevanalinks',
    packages = ['cuevanalinks',],
    license = 'GNU GENERAL PUBLIC LICENCE v3.0 (see LICENCE.txt)',
    scripts = ['bin/cuevanalinks'],
    install_requires = ['cuevanalib', 'plac>=0.8', 'progressbar'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
    options = {"py2exe": {"compressed": 2,
                          "optimize": 0, #2,
                          "includes": ['argparse', 'progressbar'],
                          "excludes": excludes,
                          "packages": ['cuevanalinks','lxml', 'gzip'],
                          "dll_excludes": dll_excludes,
                          "bundle_files": 3,
                          "dist_dir": "dist",
                          "xref": False,
                          "skip_archive": False,
                          "ascii": False,
                          "custom_boot_script": '',
                         }
              },
    console=['bin/cuevanalinks'],
)
