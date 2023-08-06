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
__version__ = "$Revision: 45490 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: MSPowerpointAttachment.py 45490 2007-07-12 08:23:45Z zegor $
__docformat__ = 'restructuredtext'


import AttachmentHandler

import os
import os.path
import string
import re
import sys

if sys.platform == "win32":
    program = "ppthtml.exe"
else:
    program = "ppthtml"


class MSPowerpointAttachment(AttachmentHandler.AbstractHandler):
    """
    MSPowerpointAttachment file abstraction
    """
    icon_file = "powerpoint.gif"
    small_icon_file = "powerpoint_small.gif"
    content_types = ('application/powerpoint', 'application/mspowerpoint', 'application/x-powerpoint', 'application/x-mspowerpoint', 'application/vnd.ms-powerpoint', )
    converter_type = "MSPowerpoint"

    is_external_conv = True
    is_working = True
    index_path = program
    index_arguments = r"%s"
    index_encoding = 'utf8'
    
    preview_path = program
    preview_arguments = r"%s"
    preview_encoding = 'utf8'
    preview_format = "html"


AttachmentHandler.registerHandler(MSPowerpointAttachment)
