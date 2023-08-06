## Validator Python Script "validate_untampered_doc"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=text=''
##title=Validates the document wasn't modified at the same time it was signed
##
if not text:
    state.setError('text', 'Input is required but no input given.', 'input_required')

if context.text != context.erase_signatures(text):
    state.setError('text', 'Document has been modified, please re-sign')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state
