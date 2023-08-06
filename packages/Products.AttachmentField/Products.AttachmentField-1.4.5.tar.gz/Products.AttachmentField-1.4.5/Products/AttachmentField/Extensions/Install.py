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
# $Id: Install.py 43145 2007-06-04 16:49:24Z glenfant $
__docformat__ = 'restructuredtext'


# Python imports
import StringIO
import string

# CMF imports
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.Extensions.utils import install_subskin

# Products imports
from Products.AttachmentField import LOG, PROJECTNAME, product_globals
from Products.AttachmentField.global_symbols import *
from Products.AttachmentField import AttachmentFieldTool

def install(self):
    out = StringIO.StringIO()

    # Install skin
    install_subskin(self, out, product_globals)

    # Install configlet
    cptool = getToolByName(self, 'portal_controlpanel')
    try:
        cptool.registerConfiglet(**attachmentfield_prefs_configlet)
    except KeyError:
        pass

    # Install tool
    add_tool = self.manage_addProduct[PROJECTNAME].manage_addTool
    tool = getattr(self, AttachmentFieldTool.AttachmentFieldTool.id, None)
    if tool is None:
        add_tool(AttachmentFieldTool.AttachmentFieldTool.meta_type)
    tool = getattr(self, AttachmentFieldTool.AttachmentFieldTool.id, None)
    print >> out, tool.migrate()
    print >> out, "Successfully installed %s." % PROJECTNAME

    return out.getvalue()

def uninstall(self):
    out = StringIO.StringIO()

    # Uninstall configlets
    try:
        cptool = getToolByName(self, 'portal_controlpanel')
        cptool.unregisterApplication(PROJECTNAME)
    except:
        LOG.info("Error at uninstall", exc_info=True)

    print >> out, "Successfully uninstalled %s." % PROJECTNAME

    return out.getvalue()

