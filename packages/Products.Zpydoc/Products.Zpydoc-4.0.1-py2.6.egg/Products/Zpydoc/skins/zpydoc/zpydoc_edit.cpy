## Controller Python Script "zpydoc_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id='',title='',description='',show_data=False,expert_mode=False
##title=edit ledger properties
##
if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)

new_context.manage_changeProperties(id=id,
                                    title=title,
                                    description=description,
                                    show_data=show_data,
                                    expert_mode=expert_mode)

from Products.CMFPlone.utils import transaction_note
transaction_note('Edited Zpydoc %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

