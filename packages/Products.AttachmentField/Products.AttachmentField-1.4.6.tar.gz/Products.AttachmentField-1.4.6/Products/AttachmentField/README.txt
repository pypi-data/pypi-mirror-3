###############
AttachmentField
###############

An Archetype field that manages file attachments, to be used in place of a FileField.

AttachmentField allows you to index and preview various kinds of documents, such as MSOffice (Word, Excel, Powerpoint), PDF and more in your Archetypes based content types.

This product replaces the former ZAttachmentAttribute from Ingeniweb (see ingeniweb.sourceforge.net).

Be sure to read the warnings below before using it.

Warning
#######

* Due to lots of misuses of AttachmentField, be warned that it does not add any new content type by itself. AttachmentField is a product for Plone/Archetypes content types developers.

* It is *strongly* discouraged to uninstall AttachmentField while configured to use FileSystemStorage. If so, all contents that use AttachmentField would be lost (even if you reinstall it later). If you want to upgrade, just reinstall it without uninstalling it.

If you need to uninstall AttachmentField, first configure it to use AttributeStorage (in ZODB) (default choice). In this case, you can then uninstall AttachmentField without loosing your content (You will need to reinstall a version of AttachmentField to access them again)

Dependencies
############

Python packages
===============

* python-libxml2

* python-libxslt

You need these packages for OpenOffice documents support.

These Python extensions are available as packages in most Linux
distros. Windows users may find a suitable libxml2 + libxslt for
Python installer from http://users.skynet.be/sbi/libxml-python/

Zope/Plone
==========

* Plone 2.1.x

* Archetypes 1.3.7+

* FileSystemStorage (only if you want to use FSS)

* Products.OpenXml (optional: for MS Office 2007 files support)

Applications/utilities (Unix)
=============================

* xpdf >= 3.0

* wvware >= 1.0

* xlhtml

* ppthtml

* unrtf >= 0.19

Applications/utilities (win32)
==============================

All above listed binary plugins are provided "batteries included" for
Windows,

The improvements / regressions of AF over ZAA are:
##################################################

* AF uses Archetypes' Field design to work. It's, then,
  Archetypes-dependent.

* ZAAPlugins is no longer necessary. All AF plugins are integrated
  directly into the AF product.

* AF offers a convenient plugin structure, allowing you to create
  plugins with only 10 lines of code. Doing so, we've lost a little
  bit of the flexibility we never needed ;) However it's still
  possible to override the AttachmentHandler class to offer more
  flexibility (AttachmentHandler is the new name for
  AbstractAttachment).

* A plugin is now a singleton providing indexing & preview & iconing
  services. No more polymorphism as in ZAA (in ZAA, each and every
  attachement stored an instance of a plugin class, which turned out
  to be too complicated for the actual need).

* A side effect of the preceding point is that you can upload invalid
  files to your server and develop (or configure) new plugins AFTER
  you've uploaded 'em. AF will dynamically detect the new content type
  and will provide preview and indexing support magically. With that
  feature, customers can start populating a website very early in the
  process!

* AF doesn't support images in MSWord preview yet (it will !)

* AF doesnt' store attachments preview nor searchable text in ZODB;
  they are cached though, and will normally be calculated only once
  per Zope program run. This may be configurable in the future
  (ie. you can choose best speed or less disk usage).

Example of use in a AT content type source
##########################################

We assume you really know Archetypes to understand this simple example...

::

  from Products.AttachmentField.AttachmentField import AttachmentField
  from Products.AttachmentField.AttachmentWidget import AttachmentWidget
  ...
  my_schema = Schema((
      ...
      AttachmentField('someFile'
                       searchable=True,
                       primary=True,
                       widget=AttachmentWidget(label="White paper",
                                               description="Your white paper for this topic",
                                               show_content_type=True)
                       )
      ...
      ))
  ...

Testing
#######

Unit tests
==========

Install PloneTestCase_ on your instance

  use testrunner -qad .

Configlet
=========

Plone managers can test the AttachmentField with the dedicated configlet.

Credits
#######

AttachmentField is an Ingeniweb_ product.

AttachmentField embeds Win32 versions of file transformation
utilities. Many thanks to the authors and maintainers of following
products:

* wvWare: http://wvware.sourceforge.net/

* xpdf (Glyph & Cog, LLC. / Foolabs): http://www.foolabs.com/xpdf/download.html

* xlhtml and ppthtml (Wrensoft): http://www.wrensoft.com/zoom/plugins.html

* unrtf: http://gnuwin32.sourceforge.net/packages/unrtf.htm

Some of theses tools require a special version of cygwin1.dll you an find in the
unrtf directory.

License
#######

AttachmentField is protected by the terms of the GPL v2 license. See
the LICENSE file for details.

Downloads
#########

You may find newer stable versions of AttachmentField and pointers to
related informations (tracker, doc, ...) from
http://plone.org/products/attachmentfield

SVN repository
##############

Stay in tune with the freshest (unstable) versions or participate to
the AttachmentField maintenance:

https://svn.plone.org/svn/collective/AttachmentField

Feedback
########

Report bugs at http://sourceforge.net/projects/ingeniweb (click the
"Bugs" link)

Ask for support at support@ingeniweb.com

-----------

.. _Ingeniweb: http://www.ingeniweb.com
.. _PloneTestCase: https://svn.plone.org/svn/collective/PloneTestCase/
