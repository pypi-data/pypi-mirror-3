## Controller Python Script "attachmentfield_test"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Test AttachmentField
##
from Products.CMFCore.utils import getToolByName

request = context.REQUEST
encoding = context.portal_properties.site_properties.default_charset
atool = getToolByName(context, 'portal_attachment')
output = atool.testFileIndexing(request.file, encoding)

return state.set(
    output = output,
    )
