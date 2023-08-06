# -*- coding: utf-8 -*-
###############################################################################
#    Bug Repo Syncer - A program to synchronize bug repositories.             #
#                                                                             #
#    Copyright (C) 2012 by Eike Welk                                          #
#    eike.welk@gmx.net                                                        #
#                                                                             #
#    License: GPL                                                             #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
###############################################################################
"""
 Setup script for the program Bug Repo Syncer 

 Install the software by issuing on the command line:
    python setup.py install

 Command line to create distributions, and upload it to PyPI:
    python setup.py sdist --formats=gztar,zip bdist --formats=rpm,wininst upload

 Small overview of frequently used commands. The command line
 generally is:
    python setup.py <command>  [--dry-run]

 Some commands are:
    sdist         : create source distribution. option:
                  :     --formats=gztar,zip 
    bdist         : create binary distribution. option:
                  :     --formats=rpm,wininst
    upload        : upload the (source) distributions to PyPI
    register      : register the project at PyPI, or change its metadata
    install       : install the software
                  :
 Global options   :
    --dry-run     : test the operation without doing anything
    --help        : show general help message
  --help-commands : show existing commands

 IMPORTANT:
 Files for the source distribution are also specified in the file:
    MANIFEST.in
"""


from distutils.core import setup
from bug_syncer.common import PROGRAM_VERSION_STR


setup(name = 'bug-repo-syncer',
      version = PROGRAM_VERSION_STR,
      author = 'Eike Welk',
      author_email = 'Eike.Welk@gmx.net',
      url = 'https://launchpad.net/bug-repo-syncer/',
      description = 'Program to synchronize bug repositories',
      long_description = open("README.txt").read(),
      license = 'GPL V3',
      packages = ['bug_syncer'],
      scripts = ['bsync'],
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Console",
                   "Intended Audience :: Developers",
                   "Intended Audience :: System Administrators",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Natural Language :: English",
                   "Operating System :: POSIX",
                   "Programming Language :: Python :: 2",
                   "Topic :: Software Development :: Quality Assurance"]
      )

