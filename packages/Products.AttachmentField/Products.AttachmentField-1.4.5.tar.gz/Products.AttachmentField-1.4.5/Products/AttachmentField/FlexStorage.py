## -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb

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

import StringIO
import itertools
from AccessControl import ClassSecurityInfo

try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.BaseUnit import BaseUnit
from Products.Archetypes.Storage import StorageLayer
from Products.Archetypes.interfaces.storage import IStorage
from Products.Archetypes.interfaces.layer import ILayer

from Products.AttachmentField import LOG

# Zope 2.7 compatibility
try:
    import transaction
    savepoint = transaction.savepoint
except ImportError:
    def savepoint(**kwargs):
         get_transaction().commit(1)

SAVEPOINT_INTERVAL = 100

## This list contains all the storage that can be used
## First data is the import statement. If import fails, the next storage is tried
## second is the storage name, and the storage class name that will be used
## third is a flog indicating if this is the default choice
SUPPORTED_FLEX_STORAGE = (
    ("from Products.Archetypes.Storage import AttributeStorage", "AttributeStorage"),
    ("from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage", "FileSystemStorage"),
)


class FlexStorage(StorageLayer):
    """
        FlexStorage is a storage proxy. It can switch between different storages for
        content on demand. In example, it can switch data from ZODB (Attribute Storage)
        to file system (FSS).
    """

    __implements__ = StorageLayer.__implements__

    ##### WARNING #####
    # All methods or attribute MUST be different from anything that can be found
    # in a storage, or it must call this method on the storage

    security = ClassSecurityInfo()

    def __init__(self):
        self.flex_storage = {}
        for storage_method, storage_name in SUPPORTED_FLEX_STORAGE:
            try:
                exec storage_method
                self.flex_storage[storage_name] = eval("%s()" % storage_name)
            except ImportError, e:
                LOG.info("%s is not installed", storage_name)

    security.declarePublic('getAvailableFlexStorages')
    def getAvailableFlexStorages(self):
        """
            Return the list of storage that are working (ie classes are found)
        """
        return self.flex_storage.keys()

    security.declarePublic('getName')
    def getName(self):
        return self.__class__.__name__

    def __repr__(self):
        return "<Storage %s>" % (self.getName())

    def __cmp__(self, other):
        return cmp(self.getName(), other.getName())


#    def __getattr__(self, name):
#        """
#            Return an attribute of the underlying storage system.
#
#            This method is only called if no attribute is found in this class.
#            It's a fallback method.
#        """
#        ## we have to check if the name is prefixed
#        print "requesting %s" % name
#        return getattr(self.getFlexStorageBackend(), name)


    security.declarePrivate('initializeInstance')
    def initializeInstance(self, instance, item=None, container=None):
        storage = self.getFlexStorageBackend(instance)
        if ILayer.isImplementedBy(storage):
            return storage.initializeInstance(instance, item, container)

    security.declarePrivate('cleanupInstance')
    def cleanupInstance(self, instance, item=None, container=None):
        storage = self.getFlexStorageBackend(instance)
        if ILayer.isImplementedBy(storage):
            return storage.cleanupInstance(instance, item, container)

    security.declarePrivate('initializeField')
    def initializeField(self, instance, field):
        storage = self.getFlexStorageBackend(instance)
        if ILayer.isImplementedBy(storage):
            return storage.initializeField(instance, field)

    security.declarePrivate('cleanupField')
    def cleanupField(self, instance, field):
        storage = self.getFlexStorageBackend(instance)
        if ILayer.isImplementedBy(storage):
            return storage.cleanupField(instance, field)

    def get(self, name, instance, **kwargs):
        storage = self.getFlexStorageBackend(instance)
        return storage.get(name, instance, **kwargs)

    def set(self, name, instance, value, **kwargs):
        return self.getFlexStorageBackend(instance).set(name, instance, value, **kwargs)

    def unset(self, name, instance, **kwargs):
        return self.getFlexStorageBackend(instance).unset(name, instance, **kwargs)

    security.declarePublic('getFlexStorageBackend')
    def getFlexStorageBackend(self, instance):
        """Return the name of the currently used storage backend

        @param instance: any zodb object to get attachent_tool by aquisition
        """
        attachment_tool = getToolByName(instance, 'portal_attachment', None)
        # XXX In unit tests dummycontent type have no context then tool
        # XXX acquisition fail. EC must fix that
        if attachment_tool is None:
            #use reasonable default value with AttributeStorage
            flex_storage_backend = SUPPORTED_FLEX_STORAGE[0][1]
        else:
            flex_storage_backend = attachment_tool.getFlexStorageBackend()

        storage = self.flex_storage.get(flex_storage_backend)
        if storage is None:
            raise RuntimeError("%s requested, but this storage has not been initialized." % flex_storage_backend)

        return storage

    security.declareProtected(CMFCorePermissions.ManagePortal, "changeFlexStorageBackend")
    def changeFlexStorageBackend(self, instance, storage_name, types):
        """Change the backend used to store data.

        Migrate the already existing fields.
        @param instance: any zodb object to get attachent_tool by aquisition
        @param storage_name: string for storage name
        @param types: dict of portal types using AttachmentField

        @return: a StringIO with nothing inside
        """
        out = StringIO.StringIO()
        attachment_tool = getToolByName(instance, 'portal_attachment')
        if attachment_tool.getFlexStorageBackend() == storage_name:
            return out.getvalue()

        old_storage = self.getFlexStorageBackend(instance)
        setattr(attachment_tool, 'flex_storage_backend',storage_name)
        new_storage = self.getFlexStorageBackend(instance)

        catalog = getToolByName(instance, 'uid_catalog')
        brains = catalog({'portal_type': types.keys()})
        izip = itertools.izip
        counter = itertools.count
        for brain, count in izip(brains, counter()):
            obj = brain.getObject()
            fields = types[obj.portal_type]
            message = self.migrateContent(old_storage, new_storage, obj, fields, out)
            print >> out, message

            if count and count % SAVEPOINT_INTERVAL == 0:
                savepoint(optimistic=True)

        return out.getvalue()

    security.declarePrivate('migrateContent')
    def migrateContent(self, old_storage, new_storage, obj, fieldnames, out):
        """Change the storage backend of one content.
            
        @param old_storage: old storage where we get the data (and remove it)
        @param new_storage: new storage where we put this data
        @param obj: object to work on it
        @param fieldnames: fields' name that are using AttachmentField
        """
        print >> out, '/'.join(obj.getPhysicalPath()), ":",

        for name in fieldnames:
            print >> out, "'%s'" % name,
            f = obj.getField(name)
            # error if field has already a content
            #if f.get_size(obj) != 0:
            #    raise RuntimeError("already set")

            # get content from old storage and delete old storage
            try:
                value = old_storage.get(name, obj)
            except AttributeError:
                print >> out, "no old value",
                continue

            # Unwrap value
            data = BaseUnit(
                name,
                str(value),
                instance=obj,
                filename=getattr(value, "filename", "unknowFilename"),
                mimetype=value.getContentType(),
            )

            ### new_storage.initializeField(content, f) #FIXME: really needed?
            f.set(obj, data)
            old_storage.unset(name, obj)
            # unset empty files, this avoid empty files on disk
            if f.get_size(obj) == 0:
                print >> out, "no data, so unset",
                f.set(obj, "DELETE_FILE")

            print >> out, ".",

