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
This module provides an abstract layer to use portal_transforms instead of external
programs to convert / preview stuff.
It's an abstract class and is meant to be overloaded in content-type specific classes.
"""
__version__ = "$Revision: 239002 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: OOAttachment.py 239002 2011-05-11 05:44:05Z ajung $
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

AVAILABLE_ENCODINGS = ('utf8', 'Latin1', )      # Default encodings

# The actual base class
class OOAttachment(AttachmentHandler.AbstractHandler):
    """
    An openoffice attachment
    """
    __CHECK_INTERFACE__ = 1
    icon_file = "oo.gif"
    small_icon_file = "oo_small.gif"
    content_types = (
        'application/vnd.sun.xml.writer',
        'application/vnd.sun.xml.writer.template',
        'application/vnd.sun.xml.writer.global',
        'application/vnd.sun.xml.calc',
        'application/vnd.sun.xml.calc.template',
        'application/vnd.sun.xml.impress',
        'application/vnd.sun.xml.impress.template',
        'application/vnd.sun.xml.draw',
        'application/vnd.sun.xml.draw.template',
        'application/vnd.sun.xml.math',
        )
    converter_type = "OpenOffice"

    is_external_conv = False
    is_working = True
    index_path = None
    index_arguments = None
    index_encoding = ("CP1252", "utf8", "latin1", )

    preview_path = None
    preview_arguments = None
    preview_format = "html"
    preview_encoding = ("CP1252", "utf8", "latin1", )

    #                                                                   #
    #              Overridable interfaces for those methods             #
    #                                                                   #

    def getIndexPath(self, field, instance):
        return "(internal)"

    def getPreviewPath(self, field, instance):
        return "(internal)"

    def getIndexableValue(self, field, instance):
        """
        getIndexableValue(self, field, instance) => (possibliy big) string
        Return the ZCatalog-indexable string for that type.
        """
        LOG.debug("getIndexableValue")
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
        LOG.debug("getPreview")
        content = field.get(instance)
        content_type = field.getContentType(instance)
        return self.convertStringToPreview(content, content_type, instance)

    def convertStringToIndex(self, content, content_type, instance):
        """
        convertStringToIndex(self, content, content_type, instance) => Utility to convert a string to HTML
        using the converter stuff.
        """
        LOG.debug("convertStringToIndex...")
        cnv = oo_to_html()
        return self._html_to_text(cnv.convert_(content,), )

    def convertStringToPreview(self, content, content_type, instance):
        """
        convertStringToPreview(self, content) => Utility to convert a string to HTML
        using the converter stuff.
        """
        LOG.debug("convertStringToPreview...")
        cnv = oo_to_html()
        return self._convertOutput(cnv.convert_(content,), "html")


##    def _convertStringToMime(self, content, content_type, instance, output_mime):
##        # Check if a transform is available

##        # Try to use / guess the encoding
##        out_encoding = out.getMetadata().get('encoding', None)
##        if out_encoding:
##            Log(LOG_DEBUG, "Have encoding", out_encoding)
##            output = unicode(output, encoding = out_encoding, )
##        else:
##            # Convert from encoded string to unicode
##            for enc in AVAILABLE_ENCODINGS:
##                try:
##                    Log(LOG_DEBUG, "Trying encoding", enc)
##                    output = output.decode(enc, )
##                    break

##                except UnicodeError:
##                    Log(LOG_DEBUG, "Encoding", enc, "failed.")
##                    pass

##        # Return an encoded output
##        return self.unicode2string(output, instance)


try:
    import libxml2
    import libxslt
except:
    LOG.warning("""libxml2 or libxslt not available. Under windows, download it at http://users.skynet.be/sbi/libxml-python/
    Open-Office indexing will be disabled.""")
else:
    from ooconverter import oo_to_html
    AttachmentHandler.registerHandler(OOAttachment)
