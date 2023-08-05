#!/usr/bin/env python
#
# Copyright (c) 2008-2012 Thomas Lotze
# See also LICENSE.txt

# indent the second line onwards to keep the PKG-INFO file format intact
"""Utilities for writing tests: sandbox directories, mock external programs,
   graphical doc-tests for cairo surfaces.
"""

import os.path
from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)

longdesc = "\n\n".join((open(project_path("README.txt")).read(),
                        open(project_path("ABOUT.txt")).read()))

install_requires = [
    'manuel>=1.0.0b3',
    "setuptools",
    ]

tests_require = [
    'mock>=0.8dev',
    "zope.testing",
    ]

extras_require = {
    "test": tests_require,
    }

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Zope Public License",
    "Programming Language :: Python",
    "Topic :: Software Development :: Testing",
    ]

setup(name="tl.testing",
      version="0.5",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords=("testing unittest doctest file directory tree sandbox helper "
                "ls mkdir mock script manuel cairo graphics image"),
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url='http://packages.python.org/tl.testing/',
      license="ZPL 2.1",
      packages=find_packages(),
      install_requires=install_requires,
      extras_require=extras_require,
      tests_require=tests_require,
      include_package_data=True,
      test_suite="tl.testing.tests.test_suite",
      namespace_packages=["tl"],
      zip_safe=False,
      )
