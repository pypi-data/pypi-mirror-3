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
__version__ = "$Revision: 76548 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: global_symbols.py 76548 2008-11-28 16:17:02Z glenfant $
__docformat__ = 'restructuredtext'


import os
import sys
import string

# Volatile or not volatile ?
_AF_VOLATILE_ = 1

# Get version
__version_file_ = open(os.path.abspath(os.path.dirname(__file__)) + '/version.txt', 'r', )
ATTACHMENTFIELD_VERSION = string.strip(__version_file_.read())
__version_file_.close()

# Text programs
if sys.platform == "win32":
    raw_conv = "type"
else:
    raw_conv = "cat"

MAX_PREVIEW_SIZE = 1024 * 5                 # If preview is larger than that, doesn't return it in the getSmallPreview() method

MAX_COLS_EXCEL = 100
MAX_ROWS_EXCEL = 100

# Configlets
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions

attachmentfield_prefs_configlet = {
    'id': 'attachmentfield_prefs',
    'appId': "AttachmentField",
    'name': 'AttachmentField Preferences',
    'action': 'string:$portal_url/attachmentfield_prefs_form',
    'category': 'Products',
    'permission': (CMFCorePermissions.ManagePortal,),
    'imageUrl': 'AttachmentField.png',
    }

# OpenXml support
try:
    import Products.OpenXml
except ImportError, e:
    HAS_OPENXML = False
else:
    HAS_OPENXML = True
