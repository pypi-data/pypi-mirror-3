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
# $Id: striphtml.py 239002 2011-05-11 05:44:05Z ajung $
__docformat__ = 'restructuredtext'

import sgmllib, string

class StrippingParser(sgmllib.SGMLParser):

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib

    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&amp;#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
        self.result = "%s&amp;%s%s" % (self.result, name, x)

    valid_tags = ('b', 'a', 'i', 'br', 'p', 'span', 'div', 'hr', 'table', 'tr', 'td', 'th', )

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:
            self.result = self.result + '&lt;' + tag
            for k, v in attrs:
                if string.lower(k[0:2]) != 'on' and string.lower(v[0:10]) != 'javascript':
                    self.result = '%s %s="%s"' % (self.result, k, v)
            endTag = '&lt;/%s&gt;' % tag
            self.endTagList.insert(0,endTag)
            self.result = self.result + '&gt;'

    def unknown_endtag(self, tag):
        if tag in self.valid_tags:
            self.result = "%s&lt;/%s&gt;" % (self.result, tag)
            remTag = '&lt;/%s&gt;' % tag
            self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
            self.result = self.result + self.endTagList[j]


def clean(s):
    parser = StrippingParser()
    parser.feed(s)
    parser.close()
    parser.cleanup()
    return parser.result


# New version

from formatter import NullFormatter
import htmllib
class ExtractText(NullFormatter):
    def __init__(self):
        NullFormatter.__init__(self)
        self.result = []

    def add_flowing_data(self, data):
        self.result.append(data)

    def add_literal_data(self, data):
        self.result.append(data)

    def bark(self):
        return "".join(self.result)

def strip(s):
    p = htmllib.HTMLParser(ExtractText())
    p.feed(s)
    return p.formatter.bark()
