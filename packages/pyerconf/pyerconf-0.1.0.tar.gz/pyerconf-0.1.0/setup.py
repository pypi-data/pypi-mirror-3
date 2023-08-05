#!/usr/bin/env python
# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <guillaume@bour.cc>"
__license__ = """
    Copyright (C) 2011, Guillaume Bour <guillaume@bour.cc>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, version 3.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from setuptools import setup, Command

setup(
    name         = 'pyerconf',
    version      = '0.1.0',
    description  = 'Pythonic Hierarchical Configuration parser',
    author       = 'Guillaume Bour',
    author_email = 'guillaume@bour.cc',
    url          = 'http://devedge.bour.cc/wiki/PyerConf',
    download_url = 'http://devedge.bour.cc/resources/pyerconf/src/pyerconf.latest.tar.gz',
    license      = 'GNU General Public License v3',
    classifiers  = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    long_description = """
Sample config::

    # a value is set with: key : value
    # values are typed. allowed types are:
    #  - string (simple or double quotes)
    #  - boolean (True or False. is case sensitive)
    #  - integer

    strval : 'this is a string'
    boolval: True
    intval : 142

    # you can define hierarchies with dictionaries
    # ! no comma to se
    orgchart : {
        boss : 'Mr Goldmine'
    
        head_office : {
            VP  : 'Miz dho'
            CTO : 'John Bugs'
        }
    }

Loaded from python::

    >>> import pyerconf
    >>> cfg = pyerconf.Config('./sample.cfg')
    >>> print cfg.strval
    this is a string
    >>> print cfg.orgchart.boss
    Mr Goldmine
    >>> print cfg.orgchart.head_office
    {'VP': 'Miz dho', 'CTO': 'John Bugs'}

    >>> print cfg.foobar
    AttributeError

    """,

    py_modules=['pyerconf'],
    install_requires=['SimpleParse']
)
