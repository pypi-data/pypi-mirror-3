## Controller Python Script "document_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Sign a document

signature = context.getMemberSignature() 
context.sign( text, signature )

from Products.CMFPlone.utils import transaction_note
transaction_note('Signed document %s at %s with %s' % (context.title_or_id(), context.absolute_url(), signature.title))

context.plone_utils.addPortalMessage('Document signed.')
return state
