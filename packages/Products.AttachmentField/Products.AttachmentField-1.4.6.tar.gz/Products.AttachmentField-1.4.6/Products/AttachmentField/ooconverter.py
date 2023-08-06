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
# $Id: ooconverter.py 239002 2011-05-11 05:44:05Z ajung $
__docformat__ = 'restructuredtext'

#                                                                                       #
#                       This code is taken from CMFOODocument                           #
#                                                                                       #
# It's provided under the following license :                                           #
#                                                                                       #
# See longsleep.org/projects/cmfoodocument                                              #
#                                                                                       #
##Zope Public License (ZPL) Version 2.0
##-----------------------------------------------

##This software is Copyright (c) Zope Corporation (tm) and
##Contributors. All rights reserved.

##This license has been certified as open source. It has also
##been designated as GPL compatible by the Free Software
##Foundation (FSF).

##Redistribution and use in source and binary forms, with or
##without modification, are permitted provided that the
##following conditions are met:

##1. Redistributions in source code must retain the above
##   copyright notice, this list of conditions, and the following
##   disclaimer.

##2. Redistributions in binary form must reproduce the above
##   copyright notice, this list of conditions, and the following
##   disclaimer in the documentation and/or other materials
##   provided with the distribution.

##3. The name Zope Corporation (tm) must not be used to
##   endorse or promote products derived from this software
##   without prior written permission from Zope Corporation.

##4. The right to distribute this software or to use it for
##   any purpose does not give you the right to use Servicemarks
##   (sm) or Trademarks (tm) of Zope Corporation. Use of them is
##   covered in a separate agreement (see
##   http://www.zope.com/Marks).

##5. If any files are modified, you must cause the modified
##   files to carry prominent notices stating that you changed
##   the files and the date of any change.

##Disclaimer

##  THIS SOFTWARE IS PROVIDED BY ZOPE CORPORATION ``AS IS''
##  AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT
##  NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
##  AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN
##  NO EVENT SHALL ZOPE CORPORATION OR ITS CONTRIBUTORS BE
##  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
##  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
##  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
##  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
##  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
##  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
##  OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
##  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
##  DAMAGE.



# imports
import Globals, string, re, os, sys, time, mimetypes
from StringIO import StringIO
from Acquisition import Implicit, aq_base, aq_parent
from OFS.Traversable import Traversable
from zope.contenttype import guess_content_type
from OFS.Image import Pdata
import libxml2, libxslt, zipfile, tempfile
from zope.interface import implements

# archetypes support
try:
    from Products.PortalTransforms.interfaces import itransform, iengine
except ImportError:
    # only works with zope2.6 and newer
    from zope.interface import Interface as itransform

try:
    import PyMagick
    isPyMagickAvailable = 1
except ImportError:
    isPyMagickAvailable = 0

try:
    import PIL.Image
    isPilAvailable = 1
except ImportError:
    isPilAvailable = 0


# set this to enable xslt debugging
_DEBUG_XSLT = 0

# add openoffice.org mime-types
_addtypes=(
            ('.sxw', 'application/vnd.sun.xml.writer'),
            ('.stw', 'application/vnd.sun.xml.writer.template'),
            ('.sxg', 'application/vnd.sun.xml.writer.global'),
            ('.sxc', 'application/vnd.sun.xml.calc'),
            ('.stc', 'application/vnd.sun.xml.calc.template'),
            ('.sxi', 'application/vnd.sun.xml.impress'),
            ('.sti', 'application/vnd.sun.xml.impress.template'),
            ('.sxd', 'application/vnd.sun.xml.draw'),
            ('.std', 'application/vnd.sun.xml.draw.template'),
            ('.sxm', 'application/vnd.sun.xml.math'),
          )
for name, val in _addtypes:
    mimetypes.types_map[name]=val

# generate openoffice mimetypes tuple
openoffice_mime_types=()
for ext, mime_type in _addtypes:
    openoffice_mime_types=openoffice_mime_types+(mime_type,)


class oo_to_html:
    """
    converter from openoffice document formats to html
    """
    implements(itransform)

    __name__ = "oo_to_html"
    inputs  = openoffice_mime_types
    output = 'text/html'

    def name(self):
        return self.__name__


    def convert_(self, data, **kwargs):
        """
        special converter for AF
        """
        # create the document dynzip extraction context
        document = DynZip(zip=data, caching=0)

        # read encoding
        encoding = kwargs.get('encoding', 'UTF-8')

        # cook it
        headers, styles, body, images = self.cook(document, encoding)

        # return it
        return body

    def convert(self, data, cache, **kwargs):
        """
        archetypes support
        """
        # create the document dynzip extraction context
        document=DynZip(zip=data, caching=0)

        # read encoding
        encoding=kwargs.get('encoding', 'UTF-8')

        # cook it
        headers, styles, body, images = self.cook(document, encoding)

        # return it inside the cache object
        cache.setData(body)

        # set the subobjects (styles, images and metadata)
        # XXX: this abuses the addSubObjects method of the AT object
        subobjects = {'headers': headers, 'styles': styles, 'images': images}
        cache.setSubObjects(subobjects)

        return cache


    def cook(self, document, encoding=None):
        """
        object usable converter
        render the document by xslt to html
        document needs to be a DynZip instance
        """

        params={}
        # default params
        packageURL='doc'
        params.update({  'absoluteSourceDirRef': "'%s'" % (packageURL)
                        , 'disableLinkedTableOfContent': 'true()'
                        , 'disableJava': 'false()'
                        , 'dpi': "'86'"
                })

        if _DEBUG_XSLT:
            params.update({'debug': 'true()'})

        # create temp files
        tmpfiles=[]
        for f in (('stylesFileURL','styles.xml'), ('metaFileURL','meta.xml')):
            # get unique filename and write contents to this file
            try:
                t=tempfile.mktemp()
                tmpfiles.append(t)
                file=open(t, 'wb', -1)
                file.write(document.read(f[1]))
                file.close()
                # update the parameters to reflect the temporary files
                params.update({f[0]: "'%s'" % (t)})
            except: pass

        # libxml2 encoding translation
        xmlOutEnc=self.getOutEncoding(default=encoding)
        # read the content xml
        thisdoc=document.read('content.xml')
        # parse the content
        doc=libxml2.parseDoc(thisdoc)
        # apply the stylesheet (xslt transformation)
        result=_style.applyStylesheet(doc, params)
        # write html to string
        html=result.serialize(encoding=xmlOutEnc)
        # free memory
        result.freeDoc()
        doc.freeDoc()

        try:
            # return parsed rendered document parts
            # (headers, styles, body, images)
            body, styles = self.parseText(html)
            images = self.parseImages(html)
            headers = self.parseMetadata(document.read('meta.xml'))
            return headers, styles, body, images

        finally:
            # clean up created temp files
            for t in tmpfiles:
                try: os.unlink(t)
                except: pass


    def parseMetadata(self, xml):
        """
        parse all metadata from xml
        """

        headers={}

        # libxml2 encoding translation
        xmlOutEnc=self.getOutEncoding(default='utf8')

        # create xpath context
        doc=libxml2.parseDoc(xml)
        ctxt=doc.xpathNewContext()

        # register openoffice xml namespaces
        ctxt.xpathRegisterNs( "office", "http://openoffice.org/2000/office")
        ctxt.xpathRegisterNs( "meta", "http://openoffice.org/2000/meta")

        # register dublincore namespace
        ctxt.xpathRegisterNs( "dc", "http://purl.org/dc/elements/1.1/")

        dict_list   = ("//meta:user-defined", "//meta:document-statistic")
        string_list = ("//meta:generator", "//dc:title", "//dc:description", "//dc:subject",
                       "//meta:creation-date", "//dc:date",
                       "//dc:language", "//meta:editing-cycles", "//meta:editing-duration")
        list_list   = ("//meta:keywords/child::meta:keyword", )

        for c in string_list:
            r = ctxt.xpathEval("%s" % c)
            name=c.split(":")[-1]
            if len(r): headers[name] = unicode(r[0].get_content(), 'UTF-8', 'replace').encode(xmlOutEnc, 'replace')

        for c in list_list:
            r = ctxt.xpathEval("%s" % c)
            name=c.split(":")[-1]
            res=[]
            for n in r:
                res.append(unicode(n.get_content(), 'UTF-8', 'replace').encode(xmlOutEnc, 'replace'))
            headers[name]=res

        # cleanup
        doc.freeDoc()
        ctxt.xpathFreeContext()

        return headers


    def parseImages(self, html):
        """
        parses all images out of the xml code
        """

        matches={}

        # create xpath context
        doc=libxml2.parseDoc(html)
        ctxt=doc.xpathNewContext()

        # get all img tags
        res=ctxt.xpathEval("//img")
        for img in res:
            try:
                width=float(img.prop('width'))
                height=float(img.prop('height'))
                matches[img.prop('src')]=(width, height)
            except:
                # most probably a linked image
                # this is not supported
                pass

        # cleanup
        doc.freeDoc()
        ctxt.xpathFreeContext()

        return matches


    def parseText(self, text):
        """
        parse the raw xml content returning headers and body
        doing xpath queries
        we assume that content is utf-8 encoded
        """

        # define vars
        styles = ''

        # libxml2 encoding translation
        xmlOutEnc=self.getOutEncoding(default='utf8')

        # create xpath context
        doc=libxml2.parseDoc(text)
        ctxt=doc.xpathNewContext()

        # get body
        res=ctxt.xpathEval("//body")
        if len(res): text=res[0].serialize(encoding=xmlOutEnc, format=1)[6:-7]

        # get styles
        res=ctxt.xpathEval("//style")
        if len(res): styles=res[0].serialize(encoding=xmlOutEnc, format=1)

        # cleanup
        doc.freeDoc()
        ctxt.xpathFreeContext()

        # return parsed parts
        return text, styles


    def getOutEncoding(self, default=None):
        """
        gets and returns encoding
        """
        encoding=None
        if not encoding and default: encoding=default
        if not encoding: encoding=sys.getdefaultencoding() # system default

        return encoding


class DynZip(Implicit, Traversable):
    """
    object to access the zipped file contents
    like images on demand emulates a dynamic container
    """

    def __init__(self, current='', zip=None, caching=0 ):
        # XXX: please comment caching
        self.current=current
        self._caching=caching
        self._zip=zip

    def _init_zip(self, data=None):
        if data: zip=data
        else: data=self._zip
        if data: return init_zip(data)
        else: return data

    def getzip(self):
        if self._zip: return self._init_zip(self._zip)
        else: return self.document(getzip=1)

    def read(self, name):
        return self.getzip().read(name)

    def close(self):
        return self.getzip().close()

    def __getitem__(self, name):
        if self.current: spacer='/'
        else: spacer=''
        name='%s%s%s' % (self.current, spacer, name)
        return DynZip(current=name, caching=self._caching).__of__(aq_parent(self))

    def __call__(self, *args, **kw):
        """
        return content of the zipfile emulating a container
        """
        if hasattr(self, 'REQUEST'):
            REQUEST=self.REQUEST
        else: REQUEST=None

        if self._caching and REQUEST:
            if not self.workingState() and self.hasImage(self.current):
                img = self.getImage(self.current)
                if img.getContentType().startswith('image'):
                    return img.__of__(aq_parent(self)).index_html(REQUEST, REQUEST.RESPONSE)

        body=self.read(self.current)
        fn=self.current.split('/')[-1]
        content_type, enc=guess_content_type(fn, body)

        if REQUEST:
            REQUEST.RESPONSE.setHeader('Content-Type', content_type)
            REQUEST.RESPONSE.setHeader('Content-Disposition', 'filename=%s' % (fn))
        return self.read(self.current)

    index_html=__call__

    def resize(self, size=None, quality=100):
        # this method returns resized images
        # pymagick or pil is supported

        path = self.current
        if not size: return self.read(path)
        width, height = size

        if isPyMagickAvailable:
            # scaling with PyMagick
            img = PyMagick.Image(str(self.read(path)), 1)
            # http://www.imagemagick.org/www/Magick++/Enumerations.html#FilterTypes
            img.filterType = PyMagick.LanczosFilter
            # resize, loosing the aspect ratio
            img.sample('%sx%s!' % (str(int(width)), str(int(height))))
            # return resized image
            return img.write()

        elif isPilAvailable:
            # scaling with pil
            image=StringIO()
            img = PIL.Image.open(StringIO(str(self.read(path))))
            fmt = img.format
            # Resize image
            img = img.resize((width, height), PIL.Image.BICUBIC)
            # Store copy in image buffer
            img.save(image, fmt, quality=quality)
            image.seek(0)
            # return image buffer
            return image.read()

        # return unscaled image
        return self.read(path)

# register system:current-time-millis xslt function
def currenttimemillis(ctx):
    # dummy method
    return "0"
libxslt.registerExtModuleFunction("current-time-millis", "http://www.jclark.com/xt/java/java.lang.System", currenttimemillis)

# load the openoffice.org to html transformation stylesheet
packageDir=Globals.package_home(globals())
__stylefile=packageDir.split(os.sep)+['converters', 'OpenOffice', 'sx2ml', 'main_html.xsl']
__stylefile='/'.join(__stylefile)
__styledoc=libxml2.parseFile(__stylefile)
_style=libxslt.parseStylesheetDoc(__styledoc)

# fill new oodocument instances with an empty openoffice.org document
__emptyoodocfile=packageDir.split(os.sep)+['_EMPTY.sxw']
__emptyoodocfile='/'.join(__emptyoodocfile)
def loadEmptyOODocument():

    try:
        try:
            doc = open(__emptyoodocfile, 'rb', -1)
            return doc.read()
        finally:
            doc.close()
    except:
        return ''


# take content and create a zipfile extraction instance
def init_zip(data):
    # XXX: how is that zipfile and stringio instance closed?
    if type(data) != type('') and type(data) != type(u'') and isinstance(data, Pdata):
        # if things get big we have Pdata to deal with
        c=data
        data=StringIO()
        next=c.next
        data.write(c.data)
        while next is not None:
            c=next
            data.write(c.data)
            next=c.next
    else:
        # else data has to be something which can be transformed to StringIO
        data=StringIO(data)

    # create zip extraction context
    return zipfile.ZipFile(data, 'rb')
