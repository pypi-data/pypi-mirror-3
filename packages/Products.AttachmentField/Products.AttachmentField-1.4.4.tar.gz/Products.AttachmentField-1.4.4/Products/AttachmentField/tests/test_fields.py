# -*- coding: utf-8 -*-
## AttachmentField
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
__version__ = "$Revision: 45993 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: test_fields.py 45993 2007-07-20 16:54:37Z glenfant $
__docformat__ = 'restructuredtext'

from os import curdir
from os.path import join, abspath, dirname, split
import os.path
import string
import re
import sets

# We need to run some methods with all permissions
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.User import UnrestrictedUser
from OFS.Image import File
from DateTime import DateTime

from Products.Archetypes.public import *
from Products.Archetypes.config import PKG_NAME
from Products.Archetypes import listTypes
from Products.Archetypes.utils import DisplayList
from Products.Archetypes import Field
from Products.Archetypes.Field import ScalableImage, Image

from Products.AttachmentField import LOG
from Products.AttachmentField.global_symbols import *
from Products.AttachmentField import AttachmentField
from Products.AttachmentField import TextAttachment, MSExcelAttachment, \
     MSWordAttachment, MSPowerpointAttachment, PDFAttachment
import IAttachmentField

from common import *
from utils import *

from test_classgen import Dummy as BaseDummy


try:
    __file__
except NameError:
    # Test was called directly, so no __file__ global exists.
    _prefix = abspath(curdir)
else:
    # Test was called by another test.
    _prefix = abspath(dirname(__file__))


# Flatten index (for test purposes)
def flattenIndex(index):
    words = []
    for w in string.split(index):
        stripped = string.lower(string.strip(w))
        if not stripped in words:
            words.append(stripped)
    words.sort
    return string.join(words, " ")


# Fields definitions
test_fields = {
    'attach_dummy': {
        'filename': 'rest1.rst',
        'icon': 'text.gif',
        'content_type': ('text/x-rst',),
        'should_index': False,
        'should_preview': False,
        },
    'attach_txt': {
        'filename': 'text.txt',
        'icon': 'text.gif',
        'content_type': TextAttachment.TextAttachment.content_types,
        'should_index': True,
        'should_preview': True,
        },
    'attach_doc': {
        'filename': 'word.doc',
        'icon': 'word.gif',
        'content_type': MSWordAttachment.MSWordAttachment.content_types,
        'should_index': True,
        'should_preview': True,
        },
    'attach_xls': {
        'filename': 'excel.xls',
        'icon': 'excel.gif',
        'content_type': MSExcelAttachment.MSExcelAttachment.content_types,
        'should_index': True,
        'should_preview': True,
        },
    'attach_ppt': {
        'filename': 'powerpoint.ppt',
        'icon': 'powerpoint.gif',
        'content_type': MSPowerpointAttachment.MSPowerpointAttachment.content_types,
        'should_index': True,
        'should_preview': True,
        },
    'attach_pdf': {
        'filename': 'adobe.pdf',
        'icon': 'pdf.gif',
        'content_type': PDFAttachment.PDFAttachment.content_types,
        'should_index': True,
        'should_preview': True,
        },
    }

# Handy structures
field_instances = []
field_values = {}
expected_values = {}
for f, info in test_fields.items():
    if info['content_type'][0].startswith('text'):
        # MIME is text/anything
        file_mode = 'rb'
    else:
        # MIME is a binary type
        file_mode ='rb'
    # Add the field
    field_instances.append(
        AttachmentField.AttachmentField(f)
        )
    field_values["%s_file" % f] = open(join(_prefix, "input", info["filename"]), file_mode)
    test_fields[f]['file'] = file(join(_prefix, "input", info["filename"]), file_mode)

    # Compute raw, index & preview
    fh = file(join(_prefix, "input", info["filename"]), file_mode)
    raw = fh.read()
    fh.close()
    test_fields[f]["expected"] = raw
    expected_values[f] = info["expected"]
    if os.path.isfile(join(_prefix, "input", info["filename"] + ".index")):
        fh = file(join(_prefix, "input", info["filename"] + ".index"))
        index = fh.read()
        fh.close()
        test_fields[f]["index"] = flattenIndex(index)
    else:
        test_fields[f]["index"] = None
    if os.path.isfile(join(_prefix, "input", info["filename"] + ".html")):
        fh = file(join(_prefix, "input", info["filename"] + ".html"))
        preview = fh.read()
        fh.close()
        test_fields[f]["preview"] = preview
    else:
        test_fields[f]["preview"] = None

schema = BaseDummy.schema + Schema(tuple(field_instances))# + BaseDummy.schema.copy()

class Dummy(BaseDummy):
    schema = schema
    def Title(self): return 'Spam' # required for ImageField


def gen_dummy():
    gen_class(Dummy, schema)


class FakeRequest:

    def __init__(self):
        self.other = {}
        self.form = {}

_nonblank_rx = re.compile(r'\S*')
def mostMatches(text1, text2, percent):
    """
    Determines if most words of text1 are in words of text2
    """
    global _nonblank_rx
    wtext1 = sets.Set([word for word in _nonblank_rx.findall(text1) if word])
    wtext2 = sets.Set([word for word in _nonblank_rx.findall(text2) if word])
    common = wtext1 & wtext2
    return len(common) > (percent * (len(wtext1) + len(wtext2)) / 2)

from Testing import ZopeTestCase
ZopeTestCase.installProduct('AttachmentField', 1)

class ProcessingTest(PloneTestCase.PloneTestCase, IAttachmentField.TestInterface):

    # tell which interfaces we check
    klasses = (AttachmentField.AttachmentField,)

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        registerType(Dummy)
        content_types, constructors, ftis = process_types(listTypes(), PKG_NAME)
        gen_dummy()
        self.makeDummy()
        self.fakeUpload()

    def makeDummy(self):
        for k, v in test_fields.items():
            v['file'].seek(0)
        self._dummy = Dummy(oid='dummy')
        self._dummy.initializeArchetype()
        return self._dummy


    def fakeUpload(self):
        current_user = getSecurityManager().getUser()
        newSecurityManager(None, UnrestrictedUser('manager', '', ['Manager'], []))
        dummy = self._dummy
        request = FakeRequest()
        request.form.update(field_values)
        dummy.REQUEST = request
        dummy.processForm(data=1)
        LOG.debug("dummy size after processForm: %d" % (
            dummy.Schema()['attach_doc'].get(dummy).getSize()))
        self._content = dummy
        newSecurityManager(None, current_user)
        
    def unHtml(self, html):
        """
        Removes HTML markup
        """
        pt = self.portal.portal_transforms
        return pt('html_to_text', html)
        

    #                                           #
    #                API Testing                #
    #                                           #

    def test_getFilename(self):
        dummy = self._content
        for k, v in test_fields.items():
            got = dummy.Schema()[k].getFilename(dummy)
            expect = v["filename"]
            self.assertEquals(got, expect,
                              'field "%s"\n got:\n %r\n\n\n expected:\n %r' % (k, got, expect))


    def test_getContentType(self):
        dummy = self._content
        for k, v in test_fields.items():
            got = dummy.Schema()[k].getContentType(dummy)
            expect = v["content_type"]
            self.failUnless(got in expect,
                            'field "%s"\n got:\n %r\n\n\n expected:\n %r' % (k, got, str(expect)))

    def test_getSize(self):
        dummy = self._content
        for k, v in test_fields.items():
            got = dummy.Schema()[k].getSize(dummy)
            expect = len(v['expected'])
            self.assertEquals(got, expect,
                              'field "%s"\n got:\n %r\n\n\n expected:\n %r' % (k, got, expect))

    # Alias such test interfaces doesn't scream stupidly
    test_get_size = test_getSize


    def test_isEmpty(self):
        dummy = self._content
        for k, v in test_fields.items():
            got = dummy.Schema()[k].isEmpty(dummy)
            expect = not len(v['expected'])
            self.assertEquals(got, expect,
                              'field "%s"\n got:\n %r\n\n\n expected:\n %r' % (k, got, expect))


    def test_getIndexableValue(self):
        dummy = self._content
        for k, v in test_fields.items():
            if not v['should_index']:
                continue
            got = dummy.Schema()[k].getIndexableValue(dummy)
            expect = v['index']
            self.failUnless(mostMatches(got, expect, 0.6),
                            'field "%s"\n got:\n %r\n\n\n expected:\n %r' % (k, got, expect))

    def test_getPreview(self):
        dummy = self._content
        for k, v in test_fields.items():
            if not v['should_preview']:
                continue
            got = dummy.Schema()[k].getPreview(dummy)
            if got:
                got = self.unHtml(got).strip()
            expect = self.unHtml(str(v['preview'])).strip()
            self.failUnless(mostMatches(got, expect, 0.6),
                            'field "%s"\n got:\n %r\n\n\n expected:\n %r' % (k, got, expect))

    def test_isPreviewAvailable(self):
        dummy = self._content
        for k, v in test_fields.items():
            if not v['should_preview']:
                continue
            got = bool(dummy.Schema()[k].isPreviewAvailable(dummy))
            expect = v['preview'] is not None
            self.assertEquals(got, expect,
                              'field "%s"\n got:\n %r\n\n\n expected:\n %r' % (k, got, expect))

    def test_isIndexed(self):
        dummy = self._content
        for k, v in test_fields.items():
            if not v['should_index']:
                continue
            self.failUnless(
                dummy.Schema()[k].isIndexed(dummy),
                'field "%s"' % k,
                )

    def test_getIcon(self, ):
        # XXX Won't test it until we install the skin in this test case !
        pass
##        #dummy = self._content
##        for k, v in test_fields.items():
##            got = dummy.Schema()[k].getIcon(dummy).getId()
##            expect = v['icon']
##            self.assertEquals(got, expect,
##                              'field "%s"\n got:\n %r\n\n\n expected:\n %r' % (k, got, expect))


    def test_getSmallIcon(self):
        """same as getIcon"""
        # XXX Won't test it until we install the skin in this test case !
        pass


    #                                           #
    #           Usual processing                #
    #                                           #

    def test_get(self):
        current_user = getSecurityManager().getUser()
        newSecurityManager(None, UnrestrictedUser('manager', '', ['Manager'], []))
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update(field_values)
        dummy.REQUEST = request
        dummy.processForm(data=1)
        for k, v in expected_values.items():
            LOG.debug(k)
            got = dummy.Schema()[k].get(dummy)
            if isinstance(got, File):
                got = str(got)
            self.assertEquals(got, v,
                              'field "%s"\n got:\n %r\n\n\n expected:\n %r' % (k, got, v))
        newSecurityManager(None, current_user)

    def test_set(self):
        """Same as previous but with fieldsets"""
        current_user = getSecurityManager().getUser()
        newSecurityManager(None, UnrestrictedUser('manager', '', ['Manager'], []))
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update(field_values)
        request.form['fieldset'] = 'default'
        dummy.REQUEST = request
        dummy.processForm()
        for k, v in test_fields.items():
            LOG.debug(k)
            got = dummy.Schema()[k].get(dummy)
            if isinstance(got, (File, ScalableImage, Image)):
                got = str(got)
            self.assertEquals(got, v['expected'],
                              'field "%s"\ngot:\n %r\n\n\n expected:\n %r' % (k, got, v['expected']))
        newSecurityManager(None, current_user)

    def test_validation(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update(field_values)
        request.form['fieldset'] = 'default'
        dummy.REQUEST = request
        errors = {}
        dummy.validate(errors=errors)
        self.failIf(errors, errors)

##    def test_required(self):
##        dummy = self.makeDummy()
##        request = FakeRequest()
##        request.form['fieldset'] = 'default'
##        f_names = []

##        schema = dummy.Schema()
##        for f in schema.fields():
##            name = f.getName()
##            f.required = 1
##            f_names.append(name)
##        errors = {}
##        dummy.validate(REQUEST=request, errors=errors)
##        self.failUnless(errors, "Errors dictionary is empty.")
##        err_fields = errors.keys()
##        failures = []
##        for f_name in f_names:
##            if f_name not in err_fields:
##                failures.append(f_name)
##        self.failIf(failures, "%s failed to report error." % failures)

    def beforeTearDown(self):
        del self._dummy
        PloneTestCase.PloneTestCase.beforeTearDown(self)




    #                                                                           #
    #                               UNUSEFUL TESTS                              #
    #                                                                           #


    def test_Vocabulary(self):
        pass

    def test_setStorage(self):
        pass

    def test_getStorage(self):
        pass

    def test_unset(self):
        # XXX TODO !!!
        pass

    def test_hasLayer(self):
        pass

    def test_registerLayer(self):
        pass

    def test_getLayerImpl(self):
        pass

    def test_registeredLayers(self):
        pass


def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ProcessingTest))
    return suite
