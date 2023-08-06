## -*- coding: utf-8 -*-
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
This module provides an abstract layer to use portal_transforms instead of external
programs to convert / preview stuff.
It's an abstract class and is meant to be overloaded in content-type specific classes.
"""
__version__ = "$Revision: 64547 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: PortalTransformsAttachment.py 64547 2008-05-07 17:07:52Z maikroeder $
__docformat__ = 'restructuredtext'


import AttachmentHandler
import DummyAttachment

import os
import os.path
import string
import re
import sys

from AccessControl import ClassSecurityInfo
import striphtml

from Products.AttachmentField import LOG
from global_symbols import *
from Products.PortalTransforms.utils import TransformException

AVAILABLE_ENCODINGS = ('utf8', 'Latin1', )      # Default encodings

transforms_cache = None


# The actual base class
class PortalTransformsAttachment(AttachmentHandler.AbstractHandler):
    """
    A portal_transforms-based attachment.
    This special kind of handler will rely on PortalTransforms to get all the relevant
    information about your stuff, such as encoding, mime types and so on.

    It does most of the work for all plugins he's aware of.
    """
    __CHECK_INTERFACE__ = 1
    preview_path = None
    preview_arguments = None
    preview_encoding = None
    preview_format = None

    index_path = None
    converter_type = "Plone Portal transform"
    icon_file = "unknow.gif"
    small_icon_file = "unknow_small.gif"
    content_types=(
        "none/none",
    )
    index_path = None
    index_arguments = None
    index_encoding = None

    is_external_conv = False
    is_working = True


    # Init method
    def getTransforms(self, field, instance):
        # Loop registered portal transforms to find those which are able to handle
        # either plain text or html conversion.

        global transforms_cache

        if transforms_cache is None:

            pt = self.getPortalTransforms(field, instance, )
            mr = self.getMimetypesRegistry(field, instance, )
            _html_paths = {}               # output: path
            _text_paths = {}               # output: path
            _all_mimes = {}
            for mime in [ str(m) for m in mr.mimetypes() ]:
                try:
                    p = pt._findPath(mime, "text/html")
                    if p:
                        _html_paths[mime] = p
                        _all_mimes[mime] = 1
                except TransformException:
                    # We ignore transform errors at this point
                    pass
                try:
                    p = pt._findPath(mime, "text/plain")
                    if p:
                        _text_paths[mime] = p
                        _all_mimes[mime] = 1
                except TransformException:
                    # We ignore transform errors at this point
                    pass

            transforms_cache = {"all_mimes": _all_mimes.keys(),
                                "html_paths": _html_paths,
                                "text_paths": _text_paths,
                               }
        return transforms_cache



    #                                                                   #
    #              Overridable interfaces for those methods             #
    #                                                                   #

    unknown_icon_file = DummyAttachment.DummyAttachment.icon_file
    unknown_small_icon_file = DummyAttachment.DummyAttachment.small_icon_file

    def getConverterType(self, field, instance):
        return "PortalTransforms"

    def getIconFile(self, field, instance):
        # We use Mimetypesregistry to get the icon path.
        # If no field has been supplied, we return a default 'unknown' icon
        if not field:
            return self.unknown_icon_file
        mime = self.getMimetypesRegistry(field, instance)
        t = mime.lookup(field.getContentType(instance))
        if not t:
            return self.unknown_icon_file
        return t[0].icon_path

    def getSmallIconFile(self, field, instance):
        # We use Mimetypesregistry to get the icon path
        # If no field has been supplied, we return a default 'unknown' icon
        if not field:
            return self.unknown_small_icon_file
        mime = self.getMimetypesRegistry(field, instance)
        t = mime.lookup(field.getContentType(instance))
        if not t:
            return self.unknown_small_icon_file
        return t[0].icon_path

    def getContentTypes(self, field, instance):
        """Return a list of the content types this tool is able to handle.
        This is quite ellaborated because we need to return only transformations with
        text/html output or pure text output.
        """
        return self.getTransforms(field, instance, )['all_mimes']

    def getIndexableValue(self, field, instance):
        """
        getIndexableValue(self, field, instance) => (possibliy big) string
        Return the ZCatalog-indexable string for that type.
        """
        content = field.get(instance)
        content_type = field.getContentType(instance)
        return self.convertStringToIndex(content, content_type, instance)

    def getPreview(self, field, instance):
        """
        getPreview(self, field, instance) => string or None

        Return the HTML preview (generating it if it's not already done) for this attachement.
        If the attachment is not previewable, or if there's a problem in the preview,
        return None.
        """
        content = field.get(instance)
        content_type = field.getContentType(instance)
        return self.convertStringToPreview(content, content_type, instance)

    def convertStringToIndex(self, content, content_type, instance):
        """
        convertStringToIndex(self, content, content_type, instance) => Utility to convert a string to HTML
        using the converter stuff.
        """
        # Convert indexer output to plain "optimized" text
        index = self._convertStringToMime(content, content_type, instance, "text/plain")
        index = striphtml.strip(index)
        words = []
        for w in string.split(index):
            stripped = string.lower(string.strip(w))
            if not stripped in words:
                words.append(stripped)
        words.sort
        return string.join(words, " ")

    def convertStringToPreview(self, content, content_type, instance):
        """
        convertStringToPreview(self, content) => Utility to convert a string to HTML
        using the converter stuff.
        """
        # Return the previewable string
        preview = self._convertStringToMime(content, content_type, instance, "text/html")
        return self._convertOutput(preview, "html")


    def _convertStringToMime(self, content, content_type, instance, output_mime):
        # Check if a transform is available
        trans = self.getTransforms(None, instance, )
        ct = content_type
        if not trans['html_paths'].get(ct, None):
            raise ValueError, "No converter found for content type '%s'" % (ct,)

        # Convert it to plain text
        pt = self.getPortalTransforms(None, instance, )
        out = pt.convertTo(
            target_mimetype = output_mime,
            orig = content,
            data = None,
            mimetype = content_type,
            )
        output = out.getData()

        # Try to use / guess the encoding
        out_encoding = out.getMetadata().get('encoding', None)
        if out_encoding:
            LOG.debug("Have encoding: '%s'" % out_encoding)
            output = unicode(output, encoding = out_encoding, )
        else:
            # Convert from encoded string to unicode
            for enc in AVAILABLE_ENCODINGS:
                try:
                    LOG.debug("Trying encoding: '%s'" % enc)
                    output = output.decode(enc, )
                    break

                except UnicodeError:
                    LOG.debug("Encoding '%s' failed" % enc)
                    pass

        # Return an encoded output
        return self.unicode2string(output, instance)

    def getSmallPreview(self,):
        """
        getSmallPreview(self,) => string or None

        Default behaviour : if the preview string is shorter than MAX_PREVIEW_SIZE, return it, else return None.
        You can override this, of course.
        """
        ret = self.getPreview()
        if not ret:
            return None
        if len(ret) < MAX_PREVIEW_SIZE:
            return ret
        return None


    #                                                                                   #
    #                                   Utility methods                                 #
    #                                                                                   #

    def getPortalTransforms(self, field, instance, ):
        """Return the portal_transforms tool"""
        return instance.portal_transforms

    def getMimetypesRegistry(self, field, instance, ):
        """Return the mimetypes_registry tool"""
        return instance.mimetypes_registry

    def _getTransformPath(self, input, output):
        """
        _getTransformPath(self, input, output) => chain or None
        Try to build a transform chain from 'input' mime type to 'output' mime type.
        If it's not possible to build such a chain, return None.
        Nota: this code is taken from TransformEngine.py
        """
        ## get a path to output mime type
        transform = self.getPortalTransforms()
        requirements = transform._policies.get(target_mt, [])
        path = transform._findPath(orig_mt, target_mt, list(requirements))

        if not path and requirements:
            LOG.debug('Unable to satisfy requirements %s' % (
                ', '.join(requirements), ))
            path = transform._findPath(orig_mt, target_mt)

        if not path:
            LOG.debug('NO PATH FROM %s TO %s : %s' % (
                orig_mt, target_mimetype, path), )
            return None
        return path

AttachmentHandler.registerHandler(PortalTransformsAttachment)
