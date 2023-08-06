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
# $Id: AttachmentHandler.py 45490 2007-07-12 08:23:45Z zegor $
__docformat__ = 'restructuredtext'


from Acquisition import Implicit
from Globals import Persistent
from Globals import MessageDialog, DTMLFile      # fakes a method from a DTML file
from AccessControl import ClassSecurityInfo
from Products.Archetypes import Field
import App.Common

import striphtml

import tempfile
import string
import cgi
import re
import sys
import os
import os.path

from Products.AttachmentField import LOG
from global_symbols import *

INVALID_VALUE = "******** INVALID VALUE *********"

# HTML Strippping variables
header_re = re.compile("(.*?<body[^>]*>)(.*?)(</body>.*)", re.S | re.I)


__HANDLERS__ = []


def registerHandler(handler_class):
    """
    registerHandler(handler_class) => register a handler class
    for a specific mime type or such.

    handler_class is a AbstractHandler-derived class
    """
    # Ensure attachmentClass conformance with the model
    if handler_class.__CHECK_INTERFACE__:
        for property in AbstractHandler.__must_derive__:
            if getattr(handler_class, property, INVALID_VALUE) == getattr(AbstractHandler, property, INVALID_VALUE):
                # Works for properties
                try:
                    raise NotImplementedError, "Attribute '%s' of class '%s' must be derived. This plugin won't be enabled." % (property, handler_class.__name__)
                except:
                    LOG("Exception occured", exc_info=True)
                    return None
            # There's nothing to enforce method-overriding, but, one day I'll put some code snippet here to do so ;-)

    # Instanciate the class
    handler = handler_class()        # We instanciate it

    if handler.is_external_conv:
        # Compute the converter and previewer paths
        index_path = handler.getIndexPath(None, None)
        preview_path = handler.getPreviewPath(None, None)
        if index_path:
            handler.index_program = getConverterProgram(
                handler
            )
        if preview_path:
            handler.preview_program = getConverterProgram(
                handler
            )
    else:
        handler.index_program = None
        handler.preview_program = None


    # Store the class
    class_name = handler_class.__name__
    __HANDLERS__.append((class_name, handler, ))
    LOG.debug("Registered '%s' class.", class_name)


def getAttachmentHandler(content_type, field, instance):
    """
    getAttachmentHandler(contentType, field, instance) => tuple(class, globs) where class is a AbstractHandler-derived class
    According to a given content type, return a class matching this kind of file
    """
    # Find a content type matching.
    LOG.debug("trying to find a handler for '%s'", content_type)
    handler = None
    for hnd in __HANDLERS__:
        if content_type in hnd[1].getContentTypes(field, instance):
            LOG.debug("We use %s" % hnd[1])
            return hnd[1]
        if hnd[0] == 'DummyAttachment':
            dummy = hnd[1]

    # No match. Have to return the dummy handler
    LOG.debug("No match, we fall back to the dummy handler '%s'", dummy)
    return dummy



class AbstractHandler(Implicit, ):
    """
    CODING INFORMATION : If you create additional methods or properties in ZAbstractAttachment that must
    be derived for the class to work, put them in the __must_derive__ tuple so that they will be checked
    at class registration. This will ensure better coding quality.

    Please note that ZAbstractAttachment-dervied objects are instanciated every time a file is uploaded.
    So you're guaranteed that the indexed file won't change during the class's lifetime.

    You can store additional files inside a ZAA with the addRelatedFile() method.
    If you want to get it back, use getRelatedFile() with the file's identifier.

    In many methods, a 'field' and 'instance' paramters are passed.
    If you're working outside an Archetypes you can pass None as 'field' and 'self' as 'instance' in
    most of the methods.
    """
    # List of methods and properties that must be derived in subclasses
    __must_derive__ = (
        "converter_type",                       # String corresponding to config.py types
        "icon_file",                            # (string) of the icon name IN A PLONE SKIN.
        "small_icon_file",                      # (string) of the SMALL icon name IN A PLONE SKIN.
        "content_types",                        # List (of strings) of content_types supported by the class

        "is_external_conv",                     # is the converter using an external programm ?
        "is_working",                           # is the converter producing anything meaningfull ?
        "index_path",                           # Index program relative path
        "index_arguments",                      # Converter program args. File name will be '%s'.
        "index_encoding",                       # Encoding managed by the encoder (output only - input is nonsence as it's most likely binary data!) or None

        "preview_path",
        "preview_arguments",                    # Preview arguments or None to disable preview
        "preview_format",                       # Previewer output format : 'text' (default) or 'html' or 'pre' (text with fixed width)
        "preview_encoding",                     # Encoding managed by the encoder (output only - input is nonsence as it's most likely binary data!) or None
        )


    # attachment properties (MUST BE DERIVEd
    converter_type = INVALID_VALUE
    icon_file = INVALID_VALUE                   # Icon file (as an instanciated Image object)
    small_icon_file = INVALID_VALUE
    content_types = INVALID_VALUE               # Supported content-types (tuple of strings)

    is_external_conv = INVALID_VALUE
    index_path = INVALID_VALUE
    index_arguments = INVALID_VALUE
    index_encoding = INVALID_VALUE

    preview_path = INVALID_VALUE
    preview_arguments = INVALID_VALUE
    preview_encoding = INVALID_VALUE
    preview_format = INVALID_VALUE

    program_found = False
    error = False ## if true, gui will display it.


    __CHECK_INTERFACE__ = 1             # Special attribute to enforce IF checking

    #                                                                   #
    #              Overridable interfaces for those methods             #
    #                                                                   #

    def initHandler(self, field, instance):
        """Initialize handler data if needed."""
        return

    def getConverterType(self, field, instance):
        return self.converter_type

    def getIconFile(self, field, instance):
        return self.icon_file

    def getSmallIconFile(self, field, instance):
        return self.small_icon_file

    def getContentTypes(self, field, instance):
        return self.content_types

    def getIndexPath(self, field, instance):
        return self.index_path

    def getIndexArguments(self, field, instance):
        return self.index_arguments

    def getIndexEncoding(self, field, instance):
        return self.index_encoding

    def getPreviewPath(self, field, instance):
        return self.preview_path

    def getPreviewArguments(self, field, instance):
        return self.preview_arguments

    def getPreviewEncoding(self, field, instance):
        return self.preview_encoding

    def getPreviewFormat(self, field, instance):
        return self.preview_format

    def getIndexableValue(self, field, instance):
        """
        getIndexableValue(self, field, instance) => (possibliy big) string
        Return the ZCatalog-indexable string for that type.
        """
        LOG.debug("converting field '%s', %s %s",
                  field.getName(), str(self.index_arguments), self.__class__.__name__)
        
        index = self._convert(
            field,
            instance,
            self.index_program,
            self.index_arguments,
            self.index_encoding,
            )

        # Convert indexer output to plain "optimized" text
        index = striphtml.strip(index)
        words = []
        for w in string.split(index):
            stripped = string.lower(string.strip(w))
            if not stripped in words:
                words.append(stripped)
        words.sort
        return string.join(words, " ")

    def convertStringToIndex(self, content, content_type, instance):
        """
        convertStringToIndex(self, content, content_type, instance) => Utility to convert a string to HTML
        using the converter stuff.
        """
        return self._convertString(
            content,
            "<string>",
            self.index_program,
            self.index_arguments,
            self.index_encoding,
            )

    def convertStringToPreview(self, content, content_type, instance):
        """
        convertStringToPreview(self, content, content_type, instance) => Utility to convert a string to HTML
        using the converter stuff.
        """
        preview = self._convertString(
            content,
            "<string>",
            self.preview_program,
            self.preview_arguments,
            self.preview_encoding,
            )
        return self._convertOutput(preview, self.preview_format)

    def _convert(self, field, instance, program, arguments, encoding):
        """
        _convert(self, field, instance, program, arguments, encoding) => call a converter with arguments. Return an unicode string.

        Won't convert if 'None' is provided as the converter or argument parameter -> This is the way for
        a plugin to inhibit conversion.
        """
        # Perform conversion
        uustring = self._convertString(
            str(field.get(instance)),
            field.getFilename(instance),
            program,
            arguments,
            encoding,
            )

        # Return an encoded string
        return Field.encode(uustring, instance)


    def unicode2string(self, str, instance):
        """Careful unicode converter"""
        return Field.encode(str, instance)

    def string2unicode(self, str, instance):
        """Careful unicode converter"""
        return Field.decode(str, instance)

    def _convertString(self, content, filename, program, arguments, encoding, ):
        """
        Utility method to convert stuff.
        This method will ALWAYS return an unicode string
        Encoding can be a string, a list, or None.
        """
        # Basic checks.
        index = ""
        if arguments is None:
            return ""
        if not program:
            return ""

        f, fn = tempfile.mkstemp()
        try:
            # Write attachment in a temporary file
            os.close(f)
            f = open(fn, "w+b")
            f.write(content)
            f.close()

            # Call converter in the right directory
            LOG.debug("Calling converter for '%s' in directory '%s'", filename, tempfile.tempdir)
            index = self.callConverter(
                program,
                arguments % (fn, ),
                )

        finally:
            # Delete attachment file
            if os.path.isfile(fn):
                os.unlink(fn)
                LOG.debug("Removed attachment file '%s'", fn)

        # Deal with various encodings
        if encoding:
            # Convert from encoded string to unicode
            if type(encoding) in (type(''), type(u''), ):
                LOG.debug("Encoding: '%s'", encoding)
                index = index.decode(encoding, "replace")

            elif type(encoding) in (type(None),):
                pass

            elif type(encoding) in (type([]), type(()), ):
                for enc in encoding:
                    try:
                        LOG.debug("Trying encoding: '%s'", enc)
                        index = index.decode(enc)
                        break

                    except UnicodeError:
                        LOG.debug("Encoding: '%s' failed", enc)
                        pass

        # Return the string
        return index


    #                                                                   #
    #                         HTML PREVIEW SUPPORT                      #
    #                                                                   #

    _strip_style = re.compile(r"""style\s*=\s*["'][^"']*["']""", re.I | re.S)
    _has_body_start = re.compile(r"""<\s*body""", re.I)
    _strip_body_start = re.compile(r""".*?<body[^>]*>""", re.I | re.S)
    _has_body_end = re.compile(r"""</\s*body""", re.I)
    _strip_body_end = re.compile(r"""</\s*body\s*>.*""", re.I | re.S)
    _strip_tags = re.compile(r"""<[^>]+>""", re.I | re.S)


    def _html_to_text(self, html):
        """crudely convert html to text"""
        LOG.debug("Stripping html tags")
        text = self._strip_tags.sub('', html, )
        LOG.debug("done.")
        return text

    def _cleanHTML(self, text):
        """
        _cleanHTML(self, text) => text
        Uses regexps to clean HTML code from various buggy attr / tags
        Return the BODY content, without 'body' tags
        """
        # Regular file size
        LOG.debug("Stripping style...")
        text = self._strip_style.sub('', text, )

        # _strip_body_start regexp may go in infinite loop
        # if there is no body attribute (in certain conditions)
        if self._has_body_start.search(text) is not None:
            LOG.debug("Stripping start tag...")
            text = self._strip_body_start.sub('', text, 1)
        if self._has_body_end.search(text) is not None:
            LOG.debug("Stripping end tag...")
            text = self._strip_body_end.sub('', text, 1)
        LOG.debug("done")
        return text.strip()

    def _convertOutput(self, preview, preview_format):
        """
        _convertOutput(self, preview, preview_format) => Convert preview to the right format,

        depending on the previewer output
        """
        if preview_format == 'text':
            # If the converter outputs plain text, we convert it into HTML
            preview = self.textToHTML(preview)

        elif preview_format == "html":
            # We just have to try to strip buggy/unuseful HTML
            preview = self._cleanHTML(preview)

        elif preview_format == "pre":
            preview = "<pre>%s</pre>" % (preview,)

        return preview

    def getPreview(self, field, instance):
        """
        getPreview(self, field, instance) => string or None

        Return the HTML preview (generating it if it's not already done) for this attachement.
        If the attachment is not previewable, or if there's a problem in the preview,
        return None.
        """
        # Check if we can preview
        if self.preview_arguments is None:
            return None

        # Call the converter with the proper arguments
        preview = self._convert(
            field,
            instance,
            self.preview_program,
            self.preview_arguments,
            self.preview_encoding,
            )
        LOG.debug("Getting preview for file '%s'", field.getFilename(instance))

        # Return the previewable string
        return self._convertOutput(preview, self.preview_format)

    def getSmallPreview(self,):
        """
        getSmallPreview(self,) => string or None

        Default behaviour : if the preview string is shorter than MAX_PREVIEW_SIZE, return it, else return None.
        You can override this, of course.
        """
        ret = self.preview()
        if not ret:
            return None
        if len(ret) < MAX_PREVIEW_SIZE:
            return ret
        return None


    #                                                                   #
    #                           UTILITY METHODS                         #
    #                                                                   #
    #   Those methods can be called from your products to make your     #
    #   work easier when creating plugins.                              #
    #                                                                   #


    def callConverter(self, program_path, arguments = '', report_errors = 1):
        """
        callConverter(self, program_path, arguments = '', report_errors = 1) => convert file using program_path with given arguments.
        Return the output stream of the converter program.

        if stdin is given, it is feed into the program. Else, it is ignored.
        if report_errors is true, 2> ~/tempfile is appended at the end of the command line
        """
        # Open read & write streams
        cmd = "%s %s" % (program_path, arguments,)
        LOG.debug("Converting file using '%s' program and '%s' arguments", 
                  program_path,
                  arguments)
        idx = ""
        err = ""
        stdout_done = 0
        stderr_done = 0

        # Manage file for error reporting
        if report_errors:
            f_, errfile = tempfile.mkstemp()
            os.close(f_)
            cmd = "%s 2> %s" % (cmd, errfile, )
        else:
            errfile = None

        # Actually execute command
        errors = ""
        curdir = os.getcwd()
        tmpdir = tempfile.mkdtemp()
        try:
            os.chdir(tmpdir)
            LOG.debug("We work in '%s'", os.getcwd())
            r = os.popen(cmd, "r")
            idx = r.read()

        finally:
            # Go back the the current dir
            os.chdir(curdir)

            # Parse error file
            if errfile:
                try:
                    f = open(errfile, "r")
                except:
                    LOG.warning("Unable to open error file '%s'", errfile)
                else:
                    errors = f.read()
                    f.close()

            # Remove the temporary directory
            try:
                for root, dirs, files in os.walk(tmpdir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(tmpdir)

            except:
                LOG.error("Could not remove temporary stuff in '%s'", tmpdir,
                          exc_info=True)

        # Report errors
        if not idx and not errors:
            raise RuntimeError, "'%s' returned nothing. No error reported by plugin. Indexing cancelled." % (cmd, )
        elif not idx:
            raise RuntimeError, "'%s' returned nothing. Error reported by plugin: '%s'. Indexing cancelled." % (cmd, errors, )
        elif idx and errors:
            LOG.warning("'%s' returned error while indexing: '%s'\nIndexing done anyway.", cmd, errors)

        LOG.debug("Conversion done. Implicitly closing streams.")

        return idx


    def textToHTML(self, text):
        """
        textToHTML(self, text) => string

        Convert a plain-text string into pretty HTML, keeping you away from the need
        to use dirty '<pre>' tags and quoting the string.
        """
        # HTML-Quote the string
        text = cgi.escape(text)

        # Convert double linefeeds into paragraphs
        # XXX TODO

        # Convert double spaces into paragraphs
        text = re.sub("  ", "&nbsp;", text, )

        # Convert simple linefeeds into line breaks
        text = re.sub("\n", "<br />\n", text, )

        # Return this pretty converted string
        text = string.strip(text)
        return text


    def getGUIIndexProgramCommand(self, field, instance):
        if not self.is_working:
            return "<em>unavailable</em>"
        if not self.is_external_conv:
            return "<em>internal</em>"
        elif self.program_found == False:
            return str(self.index_path) + " " + str(self.index_arguments) + "<br/><strong>not found</strong>"
        else:
            return str(self.index_path) + " " + str(self.index_arguments)

    def getGUIPreviewProgramCommand(self, field, instance):
        if not self.is_working:
            return "<em>unavailable</em>"
        if not self.is_external_conv:
            return "<em>internal</em>"
        elif self.program_found == False:
            return str(self.preview_path) + " " + str(self.preview_arguments) + "<br/><strong>not found</strong>"
        else:
            return str(self.preview_path) + " " + str(self.preview_arguments)

    def getError(self, field, instance):
        if self.error:
            return "error"
        return ""

#                                                                       #
#                       External programs interface                     #
#                                                                       #

PACKAGE_HOME = App.Common.package_home(globals())
if sys.platform == 'win32':
    # Windows platform
    def getConverterProgram(converter):
        conv_type = converter.converter_type
        conv_path = converter.index_path
        is_external_conv = converter.is_external_conv

        if conv_path is None:
            return None
        if conv_path.lower() == "type":
            return "type"

        program = '"' + os.path.join(PACKAGE_HOME, "converters", conv_type, "win32", conv_path, ) + '"'
        if os.path.isfile(program[1:-1]):
            LOG.debug("Using '%s' program to convert %s attachments.",
                      program, conv_type)
            converter.program_found = True
        else:
            LOG.warning(
                "Converter program '%s' not found for '%s' attachments! Indexing and preview won't work.",
                program, conv_type)

            program = None
            converter.error = True

        return program

else:
    def getConverterProgram(converter):
        conv_type = converter.converter_type
        conv_path = converter.index_path
        is_external_conv = converter.is_external_conv
        # Unix platform
        import commands
        if not is_external_conv:
            return None         # In case we don't need a program

        if "(internal)" == conv_path or conv_path is None:
            raise RuntimeError("converter path is invalid, but external conv has been set.")


        # Try to find the real full path of the program
        program = conv_path
        program = commands.getoutput("which %s" % (program))
        if not program:
            LOG.warning("Converter program '%s' not found for '%s' attachments! Indexing and preview won't work.",
                        conv_path, conv_type)
            converter.error = True
        else:
            program = string.strip(program)
            LOG.debug("Using '%s' program to convert %s attachments.",
                      program, conv_type)
            converter.program_found = True

        return program
