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
__version__ = "$Revision: 43145 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: DummyAttachment.py 43145 2007-06-04 16:49:24Z glenfant $
__docformat__ = 'restructuredtext'


from global_symbols import *

import AttachmentHandler

attach_globals = globals()

class DummyAttachment(AttachmentHandler.AbstractHandler):
    """
    ZDummyAttachment -> This class simulates an empty attachment so that ValueErrors won't be called whenever
    ZAttachmentAttribute's __underlyingFile__ will be None...
    """
    # attachment properties (MUST BE DERIVED)
    icon_file = "unknown.gif"
    small_icon_file = "unknown_small.gif"
    content_types = (None, )
    converter_type = None

    is_external_conv = False
    is_working = False
    index_path = None
    index_arguments = None
    index_encoding = None

    preview_path = None
    preview_arguments = None
    preview_encoding = None
    preview_format = None

AttachmentHandler.registerHandler(DummyAttachment)
##raise "test", AttachmentHandler.__HANDLERS__
