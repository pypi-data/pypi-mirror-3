## Controller Python Script "zpydoc_modules"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=name=''
##title=choose available modules to produce api docs for
##
request = context.REQUEST
context.manage_updateModulePermissions(request, name)

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited Zpydoc permissions %s at %s' % (context.title_or_id(), context.absolute_url()))

context.plone_utils.addPortalMessage('Module permissions updated')

if name:
     request.RESPONSE.setHeader('name', request.name)

return state

