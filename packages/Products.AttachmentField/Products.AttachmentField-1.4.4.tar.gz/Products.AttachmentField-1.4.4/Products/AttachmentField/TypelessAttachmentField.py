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
__version__ = "$Revision: 40582 $"
__docformat__ = 'restructuredtext'


# Python imports
from StringIO import StringIO
import os

# Zope imports
from AccessControl import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem, Item
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from AccessControl import Role 

# CMF imports
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.Archetypes.public import *
from Products.Archetypes.BaseObject import BaseObject

# AttachmentField imports
from global_symbols import *
import AttachmentField
import AttachmentWidget

def getTypelessAttachmentField(object):
    """getTypelessAttachmentField(self, ) => temp AF

    This method will create a temporary AF-based type in memory
    It will return the object itself.

    It must be called with 'object', which can be Plone's root.
    """
    # Basic type init
    o = TypelessAttachmentField("", )
    o.initializeArchetype()

    # Special permission handling for anonymous user
    o.manage_role(
        "Anonymous",
        [
        CMFCorePermissions.AccessContentsInformation,
        CMFCorePermissions.View,
        CMFCorePermissions.ModifyPortalContent,
        ],
        )

    # Now, return the special object
    return o.__of__(object)     #.portal_url.getPortalObject()).__of__(object)



class TypelessAttachmentField(SimpleItem, BaseObject, Role.RoleManager):
    """
    This is a sample archetype object used to manage the user's join form.
    """
    archetype_name = "TypelessAttachmentField"
    meta_type = "TypelessAttachmentField"
    isPrincipiaFolderish = 0
 
    schema = Schema(
        (
        AttachmentField.AttachmentField(
            'file',
            widget = AttachmentWidget.AttachmentWidget(
            ),
            ),
        ),
    )
    
    
registerType(TypelessAttachmentField)
