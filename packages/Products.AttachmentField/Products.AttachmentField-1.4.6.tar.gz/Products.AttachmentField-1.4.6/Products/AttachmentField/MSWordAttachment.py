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
# $Id: MSWordAttachment.py 239002 2011-05-11 05:44:05Z ajung $
__docformat__ = 'restructuredtext'


import AttachmentHandler

import os
import os.path
import string
import re
import sys

if sys.platform == "win32":
    program = "bin\\wvware.exe"
else:
    program = "wvWare"

class MSWordAttachment(AttachmentHandler.AbstractHandler):
    """
    MSWord file abstraction
    """
    icon_file = "word.gif"
    small_icon_file = "word_small.gif"
    content_types = ('application/msword', )
    converter_type = "MSWord"

    is_external_conv = True
    is_working = True
    index_path = program
    index_arguments = r"-c utf-8 -1 %s" # XXX SHOULD BE "-d DIR %s"
    index_encoding = "utf8"

    preview_path = program
    preview_arguments = r"-c utf-8 -1 %s"
    preview_format = "html"
    preview_encoding = "utf8"


# XXX TODO: BETTER PREVIEW

##def cleanHTMLcode(self, htmlcode):
##        """ Clean style attributes from HTML """
##        retidy=re.compile('style\s*=\s*([\'\"])[^\"\']*\\1',re.IGNORECASE)
##        return re.sub(retidy,'',htmlcode)



## XXX TODO: IMAGES MANAGEMENT
##
##    def convertPreview(self,):
##        """
##        Let's convert things into pretty HTML !
##        """
##        # Perform conversion and retreive files as well
##        fn = self.writeAttachmentFile()
##        try:
##            # Actual HTML conversion
##            ret = self.callConverter(arguments = "-d %s %s" % (self.getAttachmentFileDir(), fn, ))

##            # Retreive images
##            Log(LOG_DEBUG, "Temporary files:", os.listdir(self.getAttachmentFileDir()))
##            for fn in os.listdir(self.getAttachmentFileDir()):
##                ext = string.lower(string.split(fn, ".")[-1])
##                if ext in ('png', 'jpg', 'gif', 'wmz', 'wmf', 'tif', 'tiff', 'jpeg', ):
##                    filename = os.path.join(self.getAttachmentFileDir(), fn,)
##                    img = open(filename, "rb")
##                    self.addRelatedFile(fn, img.read(), "image/%s" % ext)
##                    Log(LOG_DEBUG, "Filename to delete", filename)

##                    # Close and delete file
##                    # We ignore temp file deletion problems
##                    img.close()
##                    try:        os.unlink(filename)
##                    except:     LogException()

##        finally:
##            self.deleteAttachmentFile()

##        return self.stripBody(ret)


AttachmentHandler.registerHandler(MSWordAttachment)
