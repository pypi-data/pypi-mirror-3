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
__version__ = "$Revision: 47634 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: AttachmentFieldTool.py 47634 2007-08-20 13:53:04Z encolpe $
__docformat__ = 'restructuredtext'


# Python imports
from StringIO import StringIO
import os

# Zope imports
from AccessControl import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass
from zExceptions import BadRequest
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# CMF imports
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.ActionProviderBase import ActionProviderBase

# Other imports
import AttachmentService
import AttachmentField
import FlexStorage

_www = os.path.join(os.path.dirname(__file__), 'www')

def getContentTypesWithAttachmentFields(instance):
    """
        Look for all content types that use AttachmentField, and return
        a dictionnary with
        keys : all content type names that use AttachmentField
        values : a list of all fields name that are AttachementField in
            this content type
    """
    at_tool = getToolByName(instance, 'archetype_tool')
    types = at_tool.listRegisteredTypes()
    result = {}
    for type in types:
        fields = type['schema'].fields()
        portal_type = type['portal_type']
        for field in fields:
            if isinstance(field, AttachmentField.AttachmentField) \
               and isinstance(field.storage, FlexStorage.FlexStorage):
                if portal_type in result.keys():
                    result[portal_type].append(field.getName())
                else:
                    result[portal_type] = [field.getName()]
    return result

class AttachmentFieldTool(
    UniqueObject,
    AttachmentService.AttachmentService,
    PropertyManager):
    """
    AttachmentFieldTool tool
    """

    id = 'portal_attachment'
    meta_type = 'AttachmentField Tool'
    security = ClassSecurityInfo()

    _properties = (
        {'id'  : 'contentDisposition',
         'label': "'attachment' or 'inline'",
         'type': 'selection',
         'mode': 'w',
         'select_variable' : 'getAvailableContentDisposition'
         },
        
        {'id': 'flex_storage_backend',
         'label': 'Choose backend type through the configlet',
         'type': 'string',
         'mode': 'w'
         }
        )

    # Properties values
    contentDisposition = 'attachment'
    flex_storage_backend = 'AttributeStorage'
    
    manage_options = (
        AttachmentService.AttachmentService.manage_options +
        PropertyManager.manage_options
    )

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        return self.migrate()


    security.declareProtected(CMFCorePermissions.ManagePortal, "migrate")
    def migrate(self):
        """
            Check that all properties are present and correctly initialized.
            If not, install them with a safe default value.
            It is safe to call it multiple times.
        """
        checkFor = [
            ("contentDisposition", self.getAvailableContentDisposition()[0]),
            ("flex_storage_backend", "AttributeStorage"), ## ZODB
        ]
        rValue = ""
        for attr, default in checkFor:
            if not hasattr(self, attr):
                setattr(self, attr, default)
                rValue += "Added: %s\n" % attr

        old_flex = getattr(self, 'currentFlexStorageBackend', None)
        if old_flex is not None:
            delattr(self, 'currentFlexStorageBackend')
            setattr(self, 'flex_storage_backend', old_flex)
            rValue += "Migrate: currentFlexStorageBackend\n"


        if rValue == "":
            return "Tool was already up to date."
        return rValue + "\nTool succesfully updated!"


    def getAvailableContentDisposition(self):
        return [
            "attachment",
            "inline"
        ]

    def getAvailableFlexStorageBackends(self):
        ## FlexStorage object is not singleton and doesn't hold any properties
        ## of it's own. It is safe to build on the fly instances without damage.
        return FlexStorage.FlexStorage().getAvailableFlexStorages()

    def getSample(self, type):
        sampleLinks = {
            "attachment": self.absolute_url() + "/sample/contentDispositionAttachment",
            "inline": self.absolute_url() + "/sample/contentDispositionInline",
        }
        return sampleLinks[type]

    def getContentDisposition(self):
        return self.contentDisposition

    def getFlexStorageBackend(self):
        return self.flex_storage_backend

    def setFlexStorageBackend(self, storage_name):
        ## FlexStorage object is not singleton and doesn't hold any properties
        ## of it's own. It is safe to build on the fly instances without damage.
        FlexStorage.FlexStorage().changeFlexStorageBackend(
            self,
            storage_name,
            getContentTypesWithAttachmentFields(self)
        )

    def manageDownload(self, context, traverse_subpath):
        """ Manage downlad mechanism (headers, etc)

        context: object to extract the field content from
        traverse_subpath: from Python Script is the list of subpath is under the
           script id in the URL i.e. xxx/attachment_download/file gives ['file']
        """

        request = context.REQUEST
        response = request.RESPONSE

        if len(traverse_subpath) != 1:
            raise BadRequest("Attachment download called with wrong reference.")

        field_name = traverse_subpath[0]
        field = context.getField(field_name)

        if not field:
            # CompoundField/ArrayField compatibility
            fields = context.Schema().fields()
            for fld in fields:
                separator = getattr(fld, 'separator', '')
                if separator:
                    field_names = field_name.split(separator)
                    if field_names:
                        index = int(field_names[2])
                        field = fld.getFields()[index + 1]

            if not field:
                    raise BadRequest("Attachment download called on unexistent field: %s" % field_name)

        widget = field.widget
        if hasattr(widget, "contentDisposition"):
            if widget.contentDisposition in self.getAvailableContentDisposition():
                ## disposition is defined by widget
                disposition = widget.contentDisposition
            else:
                raise ValueError(
                    "contentDisposition %s is not in %s." % (
                        widget.contentDisposition, self.getAvailableContentDisposition()
                    )
                )
        else:
            ## default site wide choice
            disposition = self.getContentDisposition()

        ## We have to force disposition to "attachment" when content type is text/*
        ## Alexander Limi said:
        ## Crucially, absolutely NO files with the MIME type text/* should ever be  
        ## rendered inline, since this opens up for uploading HTML files and using  
        ## them as spam redirection URLs. Internet Explorer renders anything with  
        ## text/* as HTML, so it is not sufficient to just block text/html,  
        ## unfortunately.

        content_type = str(field.getContentType(context))
        try:
            if content_type.startswith("text/"):
                disposition = "attachment"
        except AttributeError:
            ## Sometimes getContentType return a mimetype instead of a string
            if content_type.id.startswith("text/"):
                disposition = "attachment"

        result = field.download(context, request)

        response.setHeader(
            'Content-Disposition',
            '%s; filename="%s"' % (disposition, field.getFilename(context))
        )
        return result


InitializeClass(AttachmentFieldTool)
