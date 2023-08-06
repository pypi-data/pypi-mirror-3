# -*- coding: utf-8 -*-
## AttchmentField
## Copyright (C)2006-2007 Ingeniweb

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
AttachmentField
"""
__version__ = "$Revision: 45992 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: common.py 45992 2007-07-20 16:52:56Z glenfant $
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase

from App import config
config._config.rest_input_encoding = 'ascii'
config._config.rest_output_encoding = 'ascii'
config._config.rest_header_level = 3
del config

# Import Interface for interface testing
try:
    import Interface
except ImportError:
    # Set dummy functions and exceptions for older zope versions
    def verifyClass(iface, candidate, tentative=0):
        return True
    def verifyObject(iface, candidate, tentative=0):
        return True
    def getImplementsOfInstances(object):
        return ()
    def getImplements(object):
        return ()
    def flattenInterfaces(interfaces, remove_duplicates=1):
        return ()
    class BrokenImplementation(Execption): pass
    class DoesNotImplement(Execption): pass
    class BrokenMethodImplementation(Execption): pass
else:
    from Interface.Implements import getImplementsOfInstances, \
         getImplements, flattenInterfaces
    from Interface.Verify import verifyClass, verifyObject
    from Interface.Exceptions import BrokenImplementation, DoesNotImplement
    from Interface.Exceptions import BrokenMethodImplementation
    del Interface


class TestPreconditionFailed(Exception):
    """ Some modules are missing or other preconditions have failed """
    def __init__(self, test, precondition):
        self.test = test
        self.precondition = precondition

    def __str__(self):
        return ("Some modules are missing or other preconditions "
                "for the test %s have failed: '%s' "
                % (self.test, self.precondition))


from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl import getSecurityManager

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

if False:
    try:
        from ArchetypesTestCase import ArcheSiteTestCase
    except ImportError, err:
        ZopeTestCase._print('%s\n' % err)
        hasArcheSiteTestCase = False
    else:
        from ArchetypesTestCase import portal_name
        from ArchetypesTestCase import portal_owner
        hasArcheSiteTestCase = True

from Products.Archetypes.public import registerType, process_types, listTypes
from Products.Archetypes.config import PKG_NAME

def gen_class(klass, schema=None):
    """generats and registers the klass
    """
    if schema is not None:
        klass.schema = schema.copy()
    registerType(klass)
    content_types, constructors, ftis = process_types(listTypes(), PKG_NAME)

def mkDummyInContext(klass, oid, context, schema=None):
    gen_class(klass, schema)
    dummy = klass(oid=oid).__of__(context)
    setattr(context, oid, dummy)
    dummy.initializeArchetype()
    return dummy

from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite()
