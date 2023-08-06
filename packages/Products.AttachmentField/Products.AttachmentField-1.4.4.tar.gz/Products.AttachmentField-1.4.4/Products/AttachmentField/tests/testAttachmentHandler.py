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
__version__ = "$Revision: 45993 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: testAttachmentHandler.py 45993 2007-07-20 16:54:37Z glenfant $
__docformat__ = 'restructuredtext'

from common import *
from utils import *

from Products.AttachmentField import AttachmentHandler

class TestAbstractHandler(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.abstract_handler = AttachmentHandler.AbstractHandler()
        

    def testHtmlStripBodyStart(self):
        sample = """
        <html> <head> </head>
        <body>Stripped body start"""
        expected = """Stripped body start"""
        
        result = self.abstract_handler._strip_body_start.sub('', sample)
        self.assertEqual(result, expected)

    def testHtmlStripBodyEnd(self):
        sample = """Stripped body end</body> </html>"""
        expected = """Stripped body end"""
        result = self.abstract_handler._strip_body_end.sub('', sample)
        self.assertEqual(result, expected)

    def testCleanHTML(self):
        sample = "<html> <head> </head>\n" \
                 "<body>\n" \
                 "<h1>title</h1>\n" \
                 "<p>sample content</p>\n" \
                 "</body>\n" \
                 "</html>"

        expexted = "<h1>title</h1>\n" \
                   "<p>sample content</p>"

        result = self.abstract_handler._cleanHTML(sample)
        self.assertEqual(result, expexted)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAbstractHandler))
    return suite

