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
# $Id: MSExcelAttachment.py 239002 2011-05-11 05:44:05Z ajung $
__docformat__ = 'restructuredtext'


import AttachmentHandler

import os
import os.path
import string
import re
import sys


if sys.platform == "win32":
    program = "xlhtml.exe"
else:
    program = "xlhtml"

from Products.AttachmentField.global_symbols import MAX_ROWS_EXCEL
from Products.AttachmentField.global_symbols import MAX_COLS_EXCEL

class MSExcelAttachment(AttachmentHandler.AbstractHandler):
    """
    MSExcelAttachment file abstraction
    """
    icon_file = "excel.gif"
    small_icon_file = "excel_small.gif"
    content_types = ('application/excel', 'application/x-excel', 'application/excel', 'application/x-msexcel', 'application/vnd.ms-excel', )
    converter_type = "MSExcel"

    is_external_conv = True
    is_working = True
    index_path = program
    index_arguments = r"-xc:0-%d -xr:0-%d"%(MAX_COLS_EXCEL, MAX_ROWS_EXCEL) + r" %s"
    index_encoding = 'utf8'

    preview_path = program
    preview_arguments = r"-nh -xc:0-%d -xr:0-%d"%(MAX_COLS_EXCEL, MAX_ROWS_EXCEL) + r" %s"
    preview_format = "html"
    preview_encoding = 'utf8'


AttachmentHandler.registerHandler(MSExcelAttachment)
