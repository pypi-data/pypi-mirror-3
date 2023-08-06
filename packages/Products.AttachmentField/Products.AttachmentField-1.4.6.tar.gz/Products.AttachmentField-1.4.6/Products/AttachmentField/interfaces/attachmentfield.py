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
__version__ = "$Revision: 239002 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: attachmentfield.py 239002 2011-05-11 05:44:05Z ajung $
__docformat__ = 'restructuredtext'

from zope.interface import Attribute
try:
    from zope.interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

from Products.Archetypes.interfaces.field import IObjectField

class IAttachmentField(IObjectField):
    """ Interface for attachment-aware fields """
#     required = Attribute('required', 'Require a value to be present when submitting the field')
#     default = Attribute('default', 'Default value for a field')
#     vocabulary = Attribute('vocabulary', 'List of suggested values for the field')
#     enforceVocabulary = Attribute('enforceVocabulary', \
#                                   'Restrict the allowed values to the ones in the vocabulary')
#     multiValued = Attribute('multiValued', 'Allow the field to have multiple values')
#     searchable = Attribute('searchable', 'Make the field searchable')
#     isMetadata = Attribute('isMetadata', 'Is this field a metadata field?')
#     accessor = Attribute('accessor', 'Use this method as the accessor for the field')
#     mutator = Attribute('mutator', 'Use this method as the mutator for the field')
#     mode = Attribute('mode', 'Mode of access to this field')
#     read_permission = Attribute('read_permission', \
#                                 'Permission to use to protect field reading')
#     write_permission = Attribute('write_permission', \
#                                  'Permission to use to protect writing to the field')

#     storage = Attribute('storage', 'Storage class to use for this field')
#     form_info = Attribute('form_info', 'Form Info (?)')
#     generateMode = Attribute('generateMode', 'Generate Mode (?)')
#     force = Attribute('force', 'Force (?)')
#     type = Attribute('type', 'Type of the field')


    # Here's what we inherit from IObjectField

##    def Vocabulary(content_instance):
##        """ Vocabulary of allowed values for this field """

##    def get(instance, **kwargs):
##        """ Get the value for this field using the underlying storage """

##    def set(instance, value, **kwargs):
##        """ Set the value for this field using the underlying storage """

##    def unset(instance, **kwargs):
##        """ Unset the value for this field using the underlying storage """

##    def getStorage():
##        """ Return the storage class used in this field """

##    def setStorage(instance, storage):
##        """ Set the storage for this field to the give storage.
##        Values are migrated by doing a get before changing the storage
##        and doing a set after changing the storage.

##        The underlying storage must take care of cleaning up of removing
##        references to the value stored using the unset method."""

    def getContentType(instance,):
        """Return the type of file of this object if known (MIME type as a string);
        otherwise, return None."""

    def getIcon(instance, ):
        """Return the underlying file class icon (icon path).
        """

    def getSmallIcon(instance, ):
        """Same as getIcon but return the small version (icon path).
        """

    def getIndexableValue(instance, ):
        """Return the indexable text for this field
        """

    def isEmpty(instance, ):
        """Return true if the file is empty
        """

    def getSize(instance, ):
        """Return file size in bytes
        """

    def getFilename(instance, ):
        """Return this file's name as stored when uploading
        """

    def isIndexed(instance,):
        """Return true if the file is properly indexed
        """

    def getPreview(instance, ):
        """Return an HTML rendering of the document
        """

    def isPreviewAvailable(instance,):
        """Return true if the preview is available.
        """


    # XXX have to handle the title as well ?...
