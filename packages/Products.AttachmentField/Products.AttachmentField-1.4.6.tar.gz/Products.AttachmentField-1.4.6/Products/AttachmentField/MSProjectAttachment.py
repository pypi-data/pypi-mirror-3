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
# $Id: MSProjectAttachment.py 239002 2011-05-11 05:44:05Z ajung $
__docformat__ = 'restructuredtext'


from global_symbols import *

import os
import string
import AttachmentHandler

class MSProjectAttachment(AttachmentHandler.AbstractHandler):
    """
    MSProject file abstraction
    """
    converter_type = "MSProject"
    icon_file = "msproject.gif"
    small_icon_file = "msproject_small.gif"
    content_types = ('application/msproject', 'application/vnd.ms-project', )

    is_external_conv = False
    is_working = False
    index_path = None
    index_arguments = None
    index_encoding = None

    preview_path = None
    preview_arguments = None
    preview_encoding = None
    preview_format = None



AttachmentHandler.registerHandler(MSProjectAttachment)
