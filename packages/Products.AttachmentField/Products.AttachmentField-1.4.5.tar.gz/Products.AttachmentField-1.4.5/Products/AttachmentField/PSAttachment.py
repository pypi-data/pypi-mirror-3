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
__version__ = "$Revision: 25863 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: PSAttachment.py 25863 2006-07-07 14:47:14Z manuco $
__docformat__ = 'restructuredtext'


import AttachmentHandler

import os
import os.path
import string
import re
import sys


if sys.platform == "win32":
    program = "pstotext.exe"
else:
    program = "pstotext"


class PSAttachment(AttachmentHandler.AbstractHandler):
    """
    Postscript attachment file abstraction
    """
    icon_file = "pdf.gif"
    small_icon_file = "pdf_small.gif"
    content_types = ('application/postscript', )
    converter_type = "PS"

    is_external_conv = True
    is_working = True
    index_path = program
    index_arguments = '%s'
    index_encoding = "iso-8859-15"
    
    preview_path = program
    preview_arguments = '%s'
    preview_format = "text"
    preview_encoding = "iso-8859-15"


AttachmentHandler.registerHandler(PSAttachment)
