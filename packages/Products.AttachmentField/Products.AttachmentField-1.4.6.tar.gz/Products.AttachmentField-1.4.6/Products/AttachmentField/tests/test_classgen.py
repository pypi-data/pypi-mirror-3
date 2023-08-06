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
# $Id: test_classgen.py 239002 2011-05-11 05:44:05Z ajung $
__docformat__ = 'restructuredtext'


from common import *
from utils import *

from Products.Archetypes.public import *
from Products.Archetypes.config import PKG_NAME
from Products.Archetypes import listTypes
from Products.Archetypes.BaseUnit import BaseUnit
from Products.MimetypesRegistry.MimeTypesTool import MimeTypesTool
from Products.PortalTransforms.TransformTool import TransformTool
from Products.Archetypes.interfaces.base import IBaseUnit

from Products.CMFCore.DiscussionTool import DiscussionTool

from DateTime import DateTime
from copy import deepcopy

default_text = """
Title
=====

Subtitle
--------
"""

schema = BaseSchema + Schema((
    TextField('atextfield',
              default_content_type='text/x-rst',
              default=default_text,
              widget=RichWidget(description="Just a text field for the testing",
                                  label="A Text Field",
                                  )),

    FileField('afilefield',
              primary=1,
              widget=RichWidget(description="Just a file field for the testing",
                                  label="A File Field",
                                  )),

    LinesField('alinesfield', widget=LinesWidget),

    DateTimeField('adatefield',
                  widget=CalendarWidget(description="A date field",
                                        label="A Date Field")),

    ObjectField('anobjectfield',
                widget=StringWidget(description="An object field",
                                    label="An Object Field"),
                validators=('isURL',),
                ),

    FixedPointField('afixedpointfield',
                    widget=DecimalWidget(description="A fixed point field",
                                         label="A Fixed Point Field"),
                    ),
    StringField('awriteonlyfield', mode="w"),

    StringField('areadonlyfield', mode="r"),
    ))

class DummyDiscussionTool:
    def isDiscussionAllowedFor( self, content ):
        return False
    def overrideDiscussionFor(self, content, allowDiscussion):
        pass

class SiteProperties:
    default_charset = 'UTF-8'
    def getProperty(self, name, default=None):
        return getattr(self, name, default)

class PortalProperties:
    site_properties = SiteProperties()

class Dummy(BaseContent):
    portal_properties = PortalProperties()
    portal_discussion = DummyDiscussionTool()
    mimetypes_registry = MimeTypesTool()
    def __init__(self, oid='test', init_transforms=0, **kwargs):
        BaseContent.__init__(self, oid, **kwargs)
        self.portal_transforms = TransformTool()
        if init_transforms:
            from Products.PortalTransforms import transforms
            transforms.initialize(self.portal_transforms)

BaseUnit.portal_properties = PortalProperties()

def gen_dummy():
    gen_class(Dummy, schema)


class ClassGenTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self._dummy = mkDummyInContext(Dummy, oid='dummy', context=self.getPortal(),
                                      schema=schema)

    def test_methods(self):
        obj = self._dummy
        #setters
        self.failUnless(hasattr(obj, 'setAtextfield'))
        self.failUnless(hasattr(obj, 'setAfilefield'))
        self.failUnless(hasattr(obj, 'setAlinesfield'))
        self.failUnless(hasattr(obj, 'setAdatefield'))
        self.failUnless(hasattr(obj, 'setAnobjectfield'))
        self.failUnless(hasattr(obj, 'setAfixedpointfield'))
        self.failUnless(hasattr(obj, 'setAwriteonlyfield'))
        self.failUnless(not hasattr(obj, 'setAreadonlyfield'))
        #getters
        self.failUnless(hasattr(obj, 'getAtextfield'))
        self.failUnless(hasattr(obj, 'getAfilefield'))
        self.failUnless(hasattr(obj, 'getAlinesfield'))
        self.failUnless(hasattr(obj, 'getAdatefield'))
        self.failUnless(hasattr(obj, 'getAnobjectfield'))
        self.failUnless(hasattr(obj, 'getAfixedpointfield'))
        self.failUnless(not hasattr(obj, 'getAwriteonlyfield'))
        self.failUnless(hasattr(obj, 'getAreadonlyfield'))
        #raw getters
        self.failUnless(hasattr(obj, 'getRawAtextfield'))
        self.failUnless(hasattr(obj, 'getRawAfilefield'))
        self.failUnless(hasattr(obj, 'getRawAlinesfield'))
        self.failUnless(hasattr(obj, 'getRawAdatefield'))
        self.failUnless(hasattr(obj, 'getRawAnobjectfield'))
        self.failUnless(hasattr(obj, 'getRawAfixedpointfield'))
        self.failUnless(hasattr(obj, 'getRawAwriteonlyfield'))
        self.failUnless(not hasattr(obj, 'getRawAreadonlyfield'))

    def test_textfield(self):
        obj = self._dummy
        obj.setAtextfield('Bla', mimetype="text/plain")
        self.failUnlessEqual(str(obj.getAtextfield()), 'Bla')

    def test_filefield(self):
        obj = self._dummy
        obj.setAfilefield('Bla')
        self.failUnlessEqual(str(obj.getAfilefield()), 'Bla')

    def test_linesfield(self):
        obj = self._dummy
        obj.setAlinesfield(['Bla', 'Ble', 'Bli'])
        self.failUnlessEqual(obj.getAlinesfield(), ('Bla', 'Ble', 'Bli'))

    def test_datefield(self):
        obj = self._dummy
        obj.setAdatefield('2002/01/01')
        self.failUnlessEqual(obj.getAdatefield(), DateTime('2002/01/01'))

    def test_objectfield(self):
        obj = self._dummy
        obj.setAnobjectfield('bla')
        self.failUnlessEqual(obj.getAnobjectfield(), 'bla')

    def test_fixedpointfield(self):
        obj = self._dummy
        obj.setAfixedpointfield('26.05')
        self.failUnlessEqual(obj.getAfixedpointfield(), '26.05')

    def test_writeonlyfield(self):
        obj = self._dummy
        obj.setAwriteonlyfield('bla')
        self.failUnlessEqual(obj.getRawAwriteonlyfield(), 'bla')

    def test_getbaseunit(self):
        obj = self._dummy
        for field in obj.Schema().fields():
            if not hasattr(field,'getBaseUnit'):
                continue
            bu = field.getBaseUnit(obj)
            self.failUnless(IBaseUnit.isImplementedBy(bu),
               'Return value of %s.getBaseUnit() does not implement BaseUnit: %s' % (field.__class__, type(bu)))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ClassGenTest))
    return suite
