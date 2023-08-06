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
__version__ = "$Revision: 65264 $"
# $Id: AttachmentField.py 65264 2008-05-20 14:27:22Z encolpe $
__docformat__ = 'restructuredtext'

import urllib
import string
import os
import os.path
import sys
from types import FileType, ListType, TupleType

import Acquisition
from Acquisition import aq_base
from Globals import Persistent
from Globals import MessageDialog, DTMLFile      # fakes a method from a DTML file
from Globals import InitializeClass
from AccessControl import Role
from AccessControl import ClassSecurityInfo
from AccessControl import Permissions
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from webdav.common import rfc1123_date
import OFS.SimpleItem
from OFS.ObjectManager import ObjectManager
from OFS.Traversable import Traversable
from OFS.Image import Pdata, File

from Products.AttachmentField import LOG
from global_symbols import *
try:
    from Products.CMFCore.utils import getToolByName
except:
    pass                # No CMF -> no charset converting

from Products.Archetypes import Field
from Products.Archetypes.utils import shasattr
from Products.Archetypes.interfaces.base import IBaseUnit
from Products.Archetypes.BaseUnit import BaseUnit

from Products.AttachmentField.interfaces.attachmentfield import IAttachmentField
import AttachmentHandler

from FlexStorage import FlexStorage

##DEFAULT_ID = "attach"
##ZAA_READ_PERMISSION = Permissions.access_contents_information
##ZAA_WRITE_PERMISSION = Permissions.change_images_and_files

#if _AF_VOLATILE_:
#    _indexed_ = "_v_%s_AF_indexed"
#    _preview_ = "_v_%s_AF_preview"
#else:
#    _indexed_ = "_%s_AF_indexed"
#    _preview_ = "_%s_AF_preview"

_indexed_ = "_%s_AF_indexed"
_preview_ = "_%s_AF_preview"
_isindexed_ = "_%s_AF_isindexed"
_ispreview_ = "_%s_AF_ispreview"
_icon_ = "_%s_AF_icon"
_smallicon_ = "_%s_AF_smallicon"

# Zope 2.7 compatibility
try:
    import transaction
    savepoint = transaction.savepoint
except ImportError:
    def savepoint(**kwargs):
        get_transaction().commit(1)

class AttachmentField(Field.FileField):
    """
    A base class to handle file fields. This is based on Archetypes.
    When the file is uploaded, it's stored, as the File field, as a File class.

    See FileField.set() :

        value = File(self.getName(), '', value, mimetype)
        setattr(value, 'filename', f_name or self.getName())
        ObjectField.set(self, instance, value, **kwargs)

    """
    __implements__ = (Field.FileField.__implements__, IAttachmentField)
    security = ClassSecurityInfo()


    _properties = Field.FileField._properties.copy()
    _properties.update({
            "storage": FlexStorage()
        })


    def get(self, instance, mimetype = None, **kwargs):
        """Get value. If mime_type is 'text/plain', we retreive the
        indexed string. If it's text/html, we get the preview back.
        """
        if mimetype == 'text/plain':
            return self.getIndexableValue(instance)
        if mimetype == 'text/html':
            return self.getPreview(instance)
        kwargs.update({'mimetype': mimetype})
        return Field.FileField.get(self, instance, **kwargs)

    def set(self, instance, value, **kwargs):
        """
        Assign input value to object. If mimetype is not specified,
        pass to processing method without one and add mimetype returned
        to kwargs. Assign kwargs to instance.
        """
        ## ZEE PART 1 BEGIN
        ## XXX Here a patch for editing with Zope External Editor with all 0.9.x
        ## versions
        ## ZEE looses filename when editing and replace it by the id.
        ## This works as long as the id is not chosen or modified by an user
        request = kwargs.get('REQUEST', None)
        filename = ''
        is_bad_user_agent = False
        if request is not None:
            user_agent = request.get('HTTP_USER_AGENT', '')
            if user_agent.lower().startswith('zope external editor'):
                is_bad_user_agent = True
                filename = self.getFilename(instance)
        ## ZEE PART 1 END

        self._reset(instance)
        ret = Field.FileField.set(self, instance, value, **kwargs)

        ## ZEE PART 2 BEGIN
        ## Set the filename given before the ZEE commit
        if is_bad_user_agent:
            self.setFilename(instance, filename)
        ## ZEE PART 2 END

        return ret

    def getSize(self, instance):
        """
            getSize(self, instance) => return file size

            This method should be deprecated: now, use get_size(), as seen in
            FileField.

        """
        return self.get_size(instance)

    def isEmpty(self, instance):
        """
        return true if empty
        """
        file = self.get(instance)
        if file is None:
            return True
        if type(file) in (type(''), type(u'')):
            return not len(file)
        size = 0
        try:
            size = file.get_size()
        except:
            pass
        return not size


    def getIndexableValue(self, instance):
        """
        getIndexableValue(self, instance) => Return the value we have to index
        """
        # Emptyness check
        if self.isEmpty(instance):
            return ""

        # Is the indexing up-to-date ?
        name = self.getName()
        isindexed = hasattr(instance, _isindexed_ % name)

        if not isindexed:
            handler = self._getHandler(instance)
            idx = None
            try:
                idx = handler.getIndexableValue(self, instance)
                if idx:
                    setattr(instance, _indexed_ % name, idx)
                    setattr(instance, _isindexed_ % name, True)
            except:
                self._logException(instance)
            if not idx:
                setattr(instance, _indexed_ % name, None)
                setattr(instance, _isindexed_ % name, False)

        # Return it
        return getattr(instance, _indexed_ % name, None)

    getIndexable = getIndexableValue

    def isIndexed(self, instance):
        """return true if the document is indexed properly.
        """

        name = self.getName()
        if hasattr(instance, _isindexed_ % name):
            return getattr(instance, _isindexed_ % name, False)
        else:
            return not not self.getIndexableValue(instance)

    def isPreviewAvailable(self, instance):
        """True if a preview is available for that
        (we can compute it immediately)
        """

        name = self.getName()
        if hasattr(instance, _ispreview_ % name):
            return getattr(instance, _ispreview_ % name, False)
        else:
            return not not self.getPreview(instance)

    def isMultiValued(self, instance):
        """True if field is multi valued
        """
        return isinstance(self.get(instance), (ListType, TupleType))

    def _getHandler(self, instance):
        """
        _getHandler(self, instance) => get the handler object
        """
        handler = AttachmentHandler.getAttachmentHandler(
            self.getContentType(instance, ),
            self, instance,
            )
        return handler


    def getPreview(self, instance):
        """Return the preview for this object
        """
        if self.isEmpty(instance):
            return ""

        # Compute it if necessary
        name = self.getName()
        ispreview = hasattr(instance, _ispreview_ % name)

        if not ispreview:
            handler = self._getHandler(instance)
            preview = None
            try:
                preview = handler.getPreview(self, instance, )
                if preview:
                    setattr(instance, _preview_ % name, preview, )
                    setattr(instance, _ispreview_ % name, True, )
            except:
                self._logException(instance)

            if not preview:
                setattr(instance, _preview_ % name, None )
                setattr(instance, _ispreview_ % name, False, )

        # Return it
        return getattr(instance, _preview_ % name, None)


    def getIcon(self, instance):
        """
        getIcon(self, instance) => return the underlying file class icon (object)
        """

        name = self.getName()
        icon = getattr(instance, _icon_ % name, None)

        if not icon:
            handler = self._getHandler(instance)
            LOG.debug("getIcon for %s / %s" % (self.getFilename(instance),
                                               handler.converter_type, ))
            icon = handler.getIconFile(self, instance)
            setattr(instance, _icon_ % name, icon, )
        return getattr(instance, icon, None)

    def getSmallIcon(self, instance):
        """
        getIcon(self, instance) => return the underlying file class icon (object)
        """

        name = self.getName()
        smallicon = getattr(instance, _smallicon_ % name, None)

        if not smallicon:
            handler = self._getHandler(instance)
            smallicon = handler.getSmallIconFile(self, instance)
            setattr(instance, _smallicon_ % name, smallicon, )
        return getattr(instance, smallicon, None)

    def _reset(self, instance, ):
        """reset volatile stuff (indexation, preview)
        """
        name = self.getName()
        setattr(instance, _preview_ % name, None)
        setattr(instance, _indexed_ % name, None)
        setattr(instance, _ispreview_ % name, None)
        setattr(instance, _isindexed_ % name, None)
        setattr(instance, _icon_ % name, None)
        setattr(instance, _smallicon_ % name, None)
        delattr(instance, _isindexed_ % name)
        delattr(instance, _ispreview_ % name)

    def _logException(self, instance):
        if instance and hasattr(instance, 'getPhysicalPath'):
            path = '/'.join(instance.getPhysicalPath())
            filename = self.getFilename(instance)
            msg = 'EXCEPTION object: %s, file: %s: \n' % (path, filename)
            LOG.warning(msg, exc_info=True)
        else:
            LOG.warning('Exception occured', exc_info=True)

InitializeClass(AttachmentField)

from Products.Archetypes.Registry import registerField

registerField(
    AttachmentField,
    title='Attachment',
    description='Used for storing files with advanced features.',
)



