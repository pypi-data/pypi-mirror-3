## -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file LICENSE.txt. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id$
"""
MS Office 2007 / Mac Office 2008 files support
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import openxmllib
from openxmllib import contenttypes as ct
from Products.OpenXml.config import office_mimetypes
import AttachmentHandler

class OpenXmlBaseAttachment(AttachmentHandler.AbstractHandler):
    """Base handler for Office 2007 files"""

    __CHECK_INTERFACE__ = True
    is_external_conv = False
    is_working = True
    index_path = None
    index_arguments = None
    index_encoding = ("CP1252", "utf8", "latin1", )

    preview_path = None
    preview_arguments = None
    preview_format = "html"
    preview_encoding = ("CP1252", "utf8", "latin1", )

    @property
    def converter_type(self):
        return 'OpenXml%s' % self.filename_extension.capitalize()

    @property
    def icon_file(self):
        return self.small_icon_file

    @property
    def small_icon_file(self):
        return '%s.gif' % self.filename_extension

    def getIndexPath(self, field, instance):
        return "(internal)"

    def getPreviewPath(self, field, instance):
        return "(internal)"

    def getIndexableValue(self, field, instance):
        """
        getIndexableValue(self, field, instance) => (possibliy big) string
        Return the ZCatalog-indexable string for that type.
        """

        content = field.get(instance)
        content_type = field.getContentType(instance)
        doc = openxmllib.openXmlDocument(content.data, self.content_types[0])
        return doc.indexableText().encode(instance.getCharset(), 'replace')

    def getPreview(self, field, instance):
        return None


class OpenXmlDocm(OpenXmlBaseAttachment):
    """OOffice Word 2007 XML macro enabled document"""

    filename_extension = 'docm'
    content_types = (ct.CT_WORDPROC_DOCM_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlDocm)

class OpenXmlDocx(OpenXmlBaseAttachment):
    """Office Word 2007 XML document"""

    filename_extension = 'docx'
    content_types = (ct.CT_WORDPROC_DOCX_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlDocx)

class OpenXmlDotm(OpenXmlBaseAttachment):
    """Office Word 2007 XML macro-enabled template"""

    filename_extension = 'dotm'
    content_types = (ct.CT_WORDPROC_DOTM_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlDotm)

class OpenXmlDotx(OpenXmlBaseAttachment):
    """Office Word 2007 XML template"""

    filename_extension = 'dotx'
    content_types = (ct.CT_WORDPROC_DOTX_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlDotx)

class OpenXmlPotm(OpenXmlBaseAttachment):
    """Office Powerpoint 2007 macro-enabled XML template"""

    filename_extension = 'potm'
    content_types = (ct.CT_PRESENTATION_POTM_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlPotm)

class OpenXmlPotx(OpenXmlBaseAttachment):
    """Office Powerpoint 2007 XML template"""

    filename_extension = 'potx'
    content_types = (ct.CT_PRESENTATION_POTX_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlPotx)

class OpenXmlPpam(OpenXmlBaseAttachment):
    """Office Powerpoint 2007 macro-enabled XML add-in"""

    filename_extension = 'ppam'
    content_types = (ct.CT_PRESENTATION_PPAM_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlPpam)

class OpenXmlPpsm(OpenXmlBaseAttachment):
    """Office Powerpoint 2007 macro-enabled XML show"""

    filename_extension = 'ppsm'
    content_types = (ct.CT_PRESENTATION_PPSM_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlPpsm)

class OpenXmlPpsx(OpenXmlBaseAttachment):
    """Office Powerpoint 2007 XML show"""

    filename_extension = 'ppsx'
    content_types = (ct.CT_PRESENTATION_PPSX_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlPpsx)

class OpenXmlPptm(OpenXmlBaseAttachment):
    """Office Powerpoint 2007 macro-enabled XML presentation"""

    filename_extension = 'pptm'
    content_types = (ct.CT_PRESENTATION_PPTM_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlPptm)

class OpenXmlPptx(OpenXmlBaseAttachment):
    """Office Powerpoint 2007 XML presentation"""

    filename_extension = 'pptx'
    content_types = (ct.CT_PRESENTATION_PPTX_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlPptx)

class OpenXmlXlam(OpenXmlBaseAttachment):
    """Office Excel 2007 XML macro-enabled add-in"""

    filename_extension = 'xlam'
    content_types = (ct.CT_SPREADSHEET_XLAM_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlXlam)

class OpenXmlXlsb(OpenXmlBaseAttachment):
    """Office Excel 2007 binary workbook (BIFF12)"""

    filename_extension = 'xlsb'
    content_types = (ct.CT_SPREADSHEET_XLSB_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlXlsb)

class OpenXmlXlsm(OpenXmlBaseAttachment):
    """Office Excel 2007 XML macro-enabled workbook"""

    filename_extension = 'xlsm'
    content_types = (ct.CT_SPREADSHEET_XLSM_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlXlsm)

class OpenXmlXlsx(OpenXmlBaseAttachment):
    """Office Excel 2007 XML workbook"""

    filename_extension = 'xlsx'
    content_types = (ct.CT_SPREADSHEET_XLSX_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlXlsx)

class OpenXmlXltm(OpenXmlBaseAttachment):
    """Office Excel 2007 XML macro-enabled template"""

    filename_extension = 'xltm'
    content_types = (ct.CT_SPREADSHEET_XLTM_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlXltm)

class OpenXmlXltx(OpenXmlBaseAttachment):
    """Office Excel 2007 XML template"""

    filename_extension = 'xltx'
    content_types = (ct.CT_SPREADSHEET_XLTX_PUBLIC,)

AttachmentHandler.registerHandler(OpenXmlXltx)
