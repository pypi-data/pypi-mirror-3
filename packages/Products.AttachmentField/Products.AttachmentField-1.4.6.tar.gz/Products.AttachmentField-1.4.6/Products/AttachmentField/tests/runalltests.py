# -*- coding: utf-8 -*-
## AttchmentField
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
AttchmentField
"""
__version__ = "$Revision: 239002 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: runalltests.py 239002 2011-05-11 05:44:05Z ajung $
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

def test_finder(recurse, dir, names):
    if dir == os.curdir or '__init__.py' in names:
        parts = [x for x in dir[len(os.curdir):].split(os.sep) if x]
        tests = [x for x in names if x.startswith('test') and x.endswith('.py')]
        for test in tests:
            modpath = parts + [test[:-3]]
            m = __import__('.'.join(modpath))
            for part in modpath[1:]:
                m = getattr(m, part)
            if hasattr(m, 'test_suite'):
                suite.addTest(m.test_suite())
    if not recurse:
        names[:] = []

if __name__ == '__main__':
    os.path.walk(os.curdir, test_finder, '-R' in sys.argv)
    TestRunner().run(suite)
