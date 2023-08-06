# encoding: utf-8
# Copyright (c) 2011 AXIA Studio <info@pypapi.org>
# and Municipality of Riva del Garda TN (Italy).
#
# This file is part of PyPaPi Framework.
#
# This file may be used under the terms of the GNU General Public
# License versions 3.0 or later as published by the Free Software
# Foundation and appearing in the file LICENSE.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#

from os.path import join, split
import sys
from setuptools import setup, find_packages

# Assicurati di importare la versione dalla working directory
sys.path.insert(0, join(split(__file__)[0], 'lib'))
from pypapi import __version__

setup(name = "PyPaPi",
      version = __version__,
      description = "PyPaPi - Python and Qt Application Framework",
      author = "See COPYRIGHT file",
      author_email = "info@pypapi.org",
      license = "GPL",
      url = "http://www.pypapi.org/",
      keywords = ["application", "framework", "qt"],

      classifiers = [
        "Programming Language :: Python",
        "Development Status ::  5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        ],

      long_description = """\
PyPaPi - Python and Qt Application Framework
--------------------------------------------

A multidatabase descriptive framework for developing application
with Python and Qt toolkit.
""",

      packages = find_packages('lib'),
      package_dir = { '': 'lib' },

      scripts = ['demo/pypapi-demo.py'],

      install_requires = ['sqlalchemy >= 0.5.0rc2',
                          'zope.component >= 3.4', 'zope.interface >= 3.4',
                          'zope.schema >= 3.4', 'ZConfig >= 2.5',],

      package_data = {
        'pypapi.app': ['schema.xml'],
        'pypapi.db': ['component.xml'],
        'pypapi.ui': ['component.xml'],
        'pypapi.ui.cute': ['ui/*.ui'],
        'pypapi.lang':['*.qm'],
        'pypapidemo':['pypapidemo.conf'],
        'pypapidemo.app':['*.ui'],
      },

      zip_safe = False,

)
