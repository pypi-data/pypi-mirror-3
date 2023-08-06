##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters = content_disposition, storage_backend
##

req = context.REQUEST

atool = context.portal_attachment

atool.manage_changeProperties(contentDisposition=content_disposition)

## safe to call it with the same name
atool.setFlexStorageBackend(storage_name=storage_backend)

return state.set(status="success", portal_status_message="AttachementField configuration succesfully updated.")
