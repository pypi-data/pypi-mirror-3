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
This code snipet is used to provide useful information about IW's AttachmentField
services available (plugins, ...).

Some of this is taken from PlacelessTranslationService's logic.
"""
__version__ = "$Revision: 43145 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: AttachmentService.py 43145 2007-06-04 16:49:24Z glenfant $
__docformat__ = 'restructuredtext'



from Products.AttachmentField import LOG
from global_symbols import *

import sys, os, re, fnmatch
from types import DictType, StringType, UnicodeType
import types

import Globals
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from Globals import InitializeClass
from OFS.Folder import Folder
from ZPublisher.HTTPRequest import HTTPRequest


from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import package_home
def ptFile(id, *filename):
    if type(filename[0]) is types.DictType:
        filename = list(filename)
        filename[0] = package_home(filename[0])
    filename = os.path.join(*filename)
    if not os.path.splitext(filename)[1]:
        filename = filename + '.pt'
    return PageTemplateFile(filename, '', __name__=id)

INDEX_SAMPLE_LENGTH = 1000
import TypelessAttachmentField

class AttachmentService(Folder):
    """
    The Attachmentfield Service
    """

    meta_type = title = 'Attachment Field Service'
    icon = 'misc_/AttachmentField/AttachmentService.jpg'

    version = ATTACHMENTFIELD_VERSION
    all_meta_types = ()

    manage_options = (
        {'label': 'Info', 'action': 'manage_information'},
        )

    manage_information = ptFile(
        'manage_information',
        globals(),
        'www',
        'manage_information',
        )
    manage_testIndexing = ptFile(
        'manage_testIndexing',
        globals(),
        'www',
        'manage_testIndexing',
        )

    security = ClassSecurityInfo()

    def __init__(self, ):
        self._instance_version = ATTACHMENTFIELD_VERSION

    def isListErroneous(self):
        import AttachmentHandler

        handlers = AttachmentHandler.__HANDLERS__
        for name, handler in handlers:
            if handler.error:
                return True
        return False

    def listHandlerValues(self,):
        """
        listHandlerValues(self,) => List of attachment handlers
        """
        import AttachmentHandler

        handlers = AttachmentHandler.__HANDLERS__
        properties = (
            "preview_program",
            "index_program",
            )
        accessors = (
            ("converter_type", "getContentType", ),
            ("icon_file", "getIconFile", ),
            ("small_icon_file", "getSmallIconFile", ),
            ("content_types", "getContentTypes", ),
            ("index_path", "getIndexPath", ),
            ("index_arguments", "getIndexArguments", ),
            ("index_program_gui", "getGUIIndexProgramCommand", ),
            ("index_encoding", "getIndexEncoding", ),
            ("preview_path", "getPreviewPath", ),
            ("preview_arguments", "getPreviewArguments", ),
            ("preview_encoding", "getPreviewEncoding", ),
            ("preview_format", "getPreviewFormat", ),
            ("preview_program_gui", "getGUIPreviewProgramCommand", ),
            ("error", "getError", ),
            )

        ret = {}

        for name, handler in handlers:
            mimes = handler.getContentTypes(None, self)
            if None in mimes:
                mimes = ("(default)",)
            h = {
                "mime": mimes,
                "class": name,
                }
            for pty in properties:
                h[pty] = getattr(handler, pty, None)
            for pty, accessor in accessors:
                call = getattr(handler, accessor, None)
                if call:
                    h[pty] = call(None, self)
                else:
                    h[pty] = None
            ret[name] = h

        values = ret.values()
        values.sort(lambda x, y: cmp(x["class"], y["class"]))
        return values


    security.declareProtected(view_management_screens, "listAvailableEncodings")
    def listAvailableEncodings(self,):
        """listAvailableEncodings(self,) => Partial encodings list
        """
        return [
            "UTF8",
            "ISO-8859-1",
            "ISO-8859-15",
            "CP1252",
            "ascii",
            ]


    security.declareProtected(view_management_screens, "testFileIndexing")
    def testFileIndexing(self, file, output_encoding):
        """
        testFileIndexing(self, file, output_encoding) => dict
        the dict keys are :
          - content_type: MIME type
          - content_length: length
          - filename: filename (!)
          - raw_content: file.read()
          - index: indexable value
          - preview: html preview
          - encoding: same as output_encoding
          - obj: Typeless object
        handler id and output encoding must be provided.
        WARNING: 'handler' parameter is deprecated.
        """
        # Create a dummy object and fakely upload an attachment
        obj = TypelessAttachmentField.getTypelessAttachmentField(self)
        obj.Schema().updateAll(obj, file = file, )
        filefield = obj.getField('file')
        content_type = string.lower(file.headers['Content-Type'])
        filename = file.filename

        # Process what happens
        content = filefield.get(obj)
        filename = filefield.getFilename(obj)
        handler_mime = filefield.getContentType(obj)
        content_length = filefield.getSize(obj)
        index = filefield.getIndexableValue(obj)
        preview = filefield.getPreview(obj)
        icon_path = filefield.getIcon(obj)
        small_icon_path = filefield.getSmallIcon(obj)
        handler = filefield._getHandler(obj).__class__.__name__

        # Mangle some results to make them clearer
        if index:
            index_sample = index[:INDEX_SAMPLE_LENGTH]
            index = "%d words." % (
                len(string.split(index)),
                )
        else:
            index_sample = "(unavailable)"
            index = "(No index generated)"
        if not preview:
            preview = "(unavailable)"

        # Return a pretty results structure
        return {
            "content_type": content_type,
            "content_length": content_length,
            "filename": filename,
            "handler": handler,
            "handler_mime": handler_mime,
            "index": index,
            "index_sample": index_sample,
            "preview": preview,
            "encoding": output_encoding,
            "icon_path": icon_path,
            "small_icon_path": small_icon_path,
            "obj": obj,
            }

    security.declareProtected(view_management_screens, "_old_testFileIndexing")
    def _old_testFileIndexing(self, file, handler, output_encoding):
        """
        testFileIndexing(self, file, handler, output_encoding) => dict
        the dict keys are :
          - content_type: MIME type
          - content_length: length
          - filename: filename (!)
          - raw_content: file.read()
          - index: indexable value
          - preview: html preview
          - encoding: same as output_encoding
        handler id and output encoding must be provided.
        """
        import AttachmentHandler
        filename = file.filename
        content = file.read()
        content_type = string.lower(file.headers['Content-Type'])
        ret = {
            "content_type": content_type,
            "content_length": len(content),
            "filename": filename,
            "raw_content": content,
            "handler": "(unknown)",
            "handler_mime": "(unknown)",
            "index": "(unavailable)",
            "index_sample": "(unavailable)",
            "preview": "(unavailable)",
            "encoding": output_encoding,
            }
        handlers = AttachmentHandler.__HANDLERS__
        hnd = handler
        name = None
        mime = None

        if hnd:
            # Specific handler : get it
            for klass, handler in handlers:
                name = klass
                if name == hnd:
                    break
        else:
            # Try to guess the handler according to content-type
            handler = AttachmentHandler.getAttachmentHandler(
                content_type, None, self,
                )
            name = handler.__class__.__name__
            mime = handler.content_types

        # Ok, we've found the right handler
        ret["handler_mime"] = mime
        ret["handler"] = name
        try:
            # use the converter
            index = handler.convertStringToIndex(content, content_type, self)

            # Provide a more useable presentation
            index_sample = index[:INDEX_SAMPLE_LENGTH]
            index = "%d words." % (
                len(string.split(index)),
                )

        except:
            s = StringIO.StringIO()
            traceback.print_exc(file = s, )
            s.seek(0)
            index = s.read()
            index_sample = ""

        try:
            preview = handler.convertStringToPreview(content, content_type, self)
            preview = preview.encode(output_encoding, "replace")

        except:
            s = StringIO.StringIO()
            traceback.print_exc(file = s, )
            s.seek(0)
            preview = s.read()

        ret['index'] = index
        ret['index_sample'] = index_sample
        ret['preview'] = preview

        return ret


##    security.declareProtected(view_management_screens, 'manage_main')
##    def manage_main(self, REQUEST, *a, **kw):
##        """
##        Wrap Folder's manage_main to render international characters
##        """
##        # ugh, API cruft
##        if REQUEST is self and a:
##            REQUEST = a[0]
##            a = a[1:]
##        r = Folder.manage_main(self, self, REQUEST, *a, **kw)
##        if type(r) is UnicodeType:
##            r = r.encode('utf-8')
##        REQUEST.RESPONSE.setHeader('Content-type', 'text/html; charset=utf-8')
##        return r



InitializeClass(AttachmentService)



