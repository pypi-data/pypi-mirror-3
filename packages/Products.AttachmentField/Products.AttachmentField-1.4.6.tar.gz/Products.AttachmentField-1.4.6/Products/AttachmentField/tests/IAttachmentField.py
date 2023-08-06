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
# $Id: IAttachmentField.py 239002 2011-05-11 05:44:05Z ajung $
__docformat__ = 'restructuredtext'

import string

# Load fixture
from Testing import ZopeTestCase
from Interface import Verify

from Products.AttachmentField.interfaces.attachmentfield import IAttachmentField as SpecificInterface

def flattenList(lst):
    """
    flattenList => transform a (deep) sequence into a simple sequence
    """
    ret = []

    if type(lst) not in (type(()), type([])):
        return (lst, )

    for item in lst:
        if type(item) in (type(()), type([]), ):
            ret.extend(flattenList(item))
        else:
            ret.append(item)
    return ret

def flattenInterfaces(lst):
    """
    flattenInterfaces => fetch interfaces and inherited ones
    """
    ret = []
    lst = flattenList(lst)
    for intf in lst:
        bases = intf.getBases()
        ret.extend(flattenInterfaces(bases))
        if not intf in ret:
            ret.append(intf)
    return ret


class TestInterface(ZopeTestCase.ZopeTestCase):

    def test01Interfaces(self,):
        """
        Test that interfaces are okay
        """
        # Check interface for each and every class
        ignore = getattr(self, "ignore_interfaces", [])
        for klass in self.klasses:
            intfs = getattr(klass, "__implements__", None)
            self.failUnless(intfs, "'%s' class doesn't implement an interface!" % (klass.__name__, ))

            # Flatten interfaces
            intfs = flattenList(intfs)

            # Check each and everyone
            for intf in intfs:
                if intf in ignore:
                    continue
                self.failUnless(
                    Verify.verifyClass(
                    intf,
                    klass,
                    ),
                    "'%s' class doesn't implement '%s' interface correctly." % (klass.__name__, intf.__name__, ),
                    )


    def _test02TestCaseCompletude(self):
        """
        Check that the test case is complete : each interface entry xxx must be associated
        to a test_xxx method in the test class.
        FIXME: transforms this to warning, we're not supposed to test methods we inherit
        from FileField.
        """
        not_defined = []
        tests = dir(self)
        count = 0

        # Check interface for each and every class
        ignore = getattr(self, "ignore_interfaces", [])
        for klass in self.klasses:
            intfs = getattr(klass, "__implements__", None)
            intfs = (SpecificInterface,)
            self.failUnless(intfs, "'%s' class doesn't implement an interface!" % (klass.__name__, ))

            # Flatten interfaces
            intfs = flattenInterfaces(intfs)

            # Check each and every interface
            for intf in intfs:
                if intf in ignore:
                    continue
                for name in intf.names():
                    count += 1
                    if not "test_%s" % (name,) in tests:
                        not_defined.append("%s.%s" % (klass.__name__, name))


        # Raise in case some tests are missing
        if not_defined:
            raise RuntimeError, "%d (over %d) MISSING TESTS:\n%s do not have a test associated." % (
                len(not_defined),
                count,
                string.join(not_defined, ", "),
                )


##    def test03ClassSecurityInfo(self):
##        """
##        This method tests that each and every method has a ClassSecurityInfo() declaration
##        XXX This doesn't walk through inheritance :(
##        """
##        not_defined = []
##        count = 0

##        # Check interface for each and every class
##        ignore = getattr(self, "ignore_interfaces", [])
##        for klass in self.klasses:
##            dict = dir(klass)
##            intfs = getattr(klass, "__implements__", None)
##            self.failUnless(intfs, "'%s' class doesn't implement an interface!" % (klass.__name__, ))

##            # Flatten interfaces
##            intfs = flattenInterfaces(intfs)

##            # Now check the resulting class to see if the mapping was made
##            # correctly. Note that this uses carnal knowledge of the internal
##            # structures used to store this information!
##            # Check each method of every interface
##            for intf in intfs:
##                if intf in ignore:
##                    continue
##                for name in intf.names():
##                    count += 1
##                    if not "%s__roles__" % (name,) in dict:
##                        not_defined.append("%s.%s" % (klass.__name__, name))

##        # Raise in case some tests are missing
##        if not_defined:
##            raise RuntimeError, "%d (over %d) MISSING SECURITY DECLARATIONS:\n%s do not have a security declaration associated." % (
##                len(not_defined),
##                count,
##                string.join(not_defined, ", "),
##                )
