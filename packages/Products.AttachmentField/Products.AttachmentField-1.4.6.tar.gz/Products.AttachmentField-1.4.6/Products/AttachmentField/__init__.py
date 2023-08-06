# -*- coding: utf-8 -*-
## AttachmentField
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
AttachmentField
"""
__version__ = "$Revision: 249757 $"
__docformat__ = 'restructuredtext'

import os.path
import logging
LOG = logging.getLogger('AttachmentField')

if os.path.isfile(os.path.join(__path__[0], 'debug.txt')):
    LOG.setLevel(logging.DEBUG)

LOG.info("Logging level set to %s" , (
    logging.getLevelName(LOG.getEffectiveLevel()),)
         )

import Globals
from AccessControl import ModuleSecurityInfo, allow_module

import AccessControl.Permissions
import AttachmentField

from global_symbols import *

from AccessControl.Permissions import *

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions
PROJECTNAME = "AttachmentField"

registerDirectory('skins', globals())
registerDirectory('skins/attachmentfield', globals())

product_globals = globals()          # Used only in the Extensions/Install.py script

# Old and deprecated service management
cp_id = "AttachmentService"

def initialize(context):

    # Previous versions of AttachmentField put an "AttachmentService" in zope
    # control panel. We remove it if it is still present
    #cp = context._ProductContext__app.Control_Panel # argh
    #if cp_id in cp.objectIds():
    #    cp._delObject(cp_id)

    # Import tool
    from Products.AttachmentField.AttachmentFieldTool import AttachmentFieldTool
    utils.ToolInit(
        PROJECTNAME + ' Tool',
        tools=(AttachmentFieldTool,),
#        product_name=PROJECTNAME,
        icon='tool.gif').initialize(context)


# Plugins MUST BE IMPORTED LAST !
# XXX TODO : we should provide a way to automatically import services
# (like Zope's 'Products' dir)
import AudioAttachment
import AutocadAttachment
import DummyAttachment
import HTMLAttachment
import ImageAttachment
import MSAccessAttachment
import MSExcelAttachment
import MSPowerpointAttachment
import MSProjectAttachment
import MSWordAttachment
import PDFAttachment
import TextAttachment
import VisioAttachment
import ZipAttachment
import VideoAttachment
import CompressedAttachment
import TarGzAttachment
import RTFAttachment
import OOAttachment
import OO2Attachment
import PSAttachment
import FlashAttachment
import PhotoshopAttachment
if HAS_OPENXML:
    import OpenXmlAttachment
import PortalTransformsAttachment
