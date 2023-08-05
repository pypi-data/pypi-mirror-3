#!/usr/bin/env python
#
# Copyright (c) 2007-2012 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe for creating a virtual Python installation
"""

import os.path
import glob

from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)


entry_points = {
    "zc.buildout": [
    "default = tl.buildout_virtual_python.base:Recipe",
    ],
    }

longdesc = "\n\n".join((open(project_path("README.txt")).read(),
                        open(project_path("ABOUT.txt")).read()))

data_files = [("", glob.glob(project_path("*.txt")))]

install_requires = [
    "setuptools",
    "virtualenv",
    "zc.buildout",
    "zc.recipe.egg",
    ]

classifiers = [
    "Environment :: Console",
    "Environment :: Plugins",
    "Framework :: Buildout",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Zope Public License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 2 :: Only",
    "Topic :: Software Development :: Build Tools",
    "Topic :: System :: Software Distribution",
    ]

setup(name="tl.buildout_virtual_python",
      version="0.2",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords=("buildout zc.buildout recipe "
                "virtual python environment virtualenv"),
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://www.thomas-lotze.de/en/software/buildout-recipes/",
      license="ZPL 2.1",
      packages=find_packages(),
      namespace_packages=["tl"],
      entry_points=entry_points,
      install_requires=install_requires,
      include_package_data=True,
      data_files=data_files,
      zip_safe=True,
      )
