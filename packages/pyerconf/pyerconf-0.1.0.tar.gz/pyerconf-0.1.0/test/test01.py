#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    XXXreblok, python decompiler, AST builder
    Copyright (C) 2011, Guillaume Bour <guillaume@bour.cc>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__author__  = "Guillaume Bour <guillaume@bour.cc>"
__version__ = "$Revision$"
__date__    = "$Date$"
__license__ = "GPLv3"

import unittest
import config

class TestConfig(unittest.TestCase):
    def test01_config(self):
        c = config.Config('test01.cfg')
        print dir(c)
        c.plop = 'truc'
        c.core = 'toto'
        print dir(c), c.plop, c.core

        self.assertTrue(hasattr(c, 'core'))
        self.assertTrue(hasattr(c, 'channels'))
        self.assertTrue(hasattr(c.core, 'database'))

        self.assertEqual(c.core.database, 'plop.db')
        self.assertTrue(isinstance(c.channels.rss, dict))
        self.assertTrue(isinstance(c.channels.rss.url, str))
        self.assertTrue(isinstance(c.channels.rss.refresh, int))
        self.assertTrue(isinstance(c.channels.rss.active, bool))

if __name__ == '__main__':
    unittest.main()

