#!/usr/bin/env python

import sys
import os
from os.path import join

from distutils.core import setup

from dreampielib import __version__, subp_lib

# What's non-standard about installing DreamPie is:
# * There are automatically generated modules, in dreampielib/data.
#   These are generated whenever the setup.py script is run, so from the
#   distutils point of view these files are regular package data files.
# * py2exe doesn't support package data, so "regular" data_files are used,
#   and the 'data' directory ends up near the executable.

subp_lib.build()

if 'py2exe' in sys.argv:
    import py2exe
else:
    py2exe = None

# TODO: What's this?
#if py2exe is not None:
#    # Generate needed wrappers
#    from comtypes.client import CreateObject
#    ws = CreateObject("WScript.Shell")

package_data_files = (['data/dreampie.glade',
                       'data/dreampie.png',
                       'data/subp_main.py'] + 
                      [join('data', libfn, fn)
                       for libfn in subp_lib.lib_fns.values()
                       for fn in subp_lib.files])

if py2exe is not None:
    # Add files normally installed in package_data to data_files
    d = {}
    for fn in package_data_files:
        d.setdefault(os.path.dirname(fn), []).append(join('dreampielib', fn))
    additional_py2exe_data_files = d.items()
else:
    additional_py2exe_data_files = []


setup_args = dict(
    name='dreampie',
    version=__version__,
    description="DreamPie - The interactive Python shell you've always dreamed about!",
    author='Noam Yorav-Raphael',
    author_email='noamraph@gmail.com',
    url='http://dreampie.sourceforge.net/',
    license='GPL v3+',
    scripts=['dreampie'],
    packages=['dreampielib',
              'dreampielib.common', 'dreampielib.gui', 'dreampielib.subprocess',
              ],
    package_data={'dreampielib': package_data_files},
    data_files=[
                ('share/applications', ['share/applications/dreampie.desktop']),
                ('share/man/man1', ['share/man/man1/dreampie.1']),
                ('share/pixmaps', ['share/pixmaps/dreampie.svg',
                                   'share/pixmaps/dreampie.png']),
               ] + additional_py2exe_data_files,
    )

if py2exe is not None:
    setup_args.update(dict(
        console=[{'script': 'dreampie.py',
                  'icon_resources': [(1, 'dreampie.ico')]}],
        windows=[{'script': 'create-shortcuts.py',
                  'icon_resources': [(1, 'blank.ico')]}],
        options={'py2exe':
                 {'ignores':['_scproxy', 'glib', 'gobject', 'gtk',
                             'gtk.gdk', 'gtk.glade', 'gtksourceview2',
                             'pango', 'pygtk'],
                  'excludes':['_ssl', 'doctest', 'pdb', 'unittest', 'difflib',
                              'unicodedata', 'bz2', 'zipfile', 'lib2to3'],
                  'includes':['fnmatch', 'glob'],
                 }},
    ))

setup(**setup_args)
