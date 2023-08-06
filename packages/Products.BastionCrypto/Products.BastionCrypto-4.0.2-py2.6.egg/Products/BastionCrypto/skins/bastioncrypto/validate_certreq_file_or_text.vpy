## Validator Python Script "validate_certreq_file_or_text"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=keyfile=None,keytext=''
##title=Validates that either keyfile or keytext has been sent in the request
##
if not keyfile and not keytext:
    # we are just flagging this ...
    state.setError('keyfile', 'file not input')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please send either file or text!', 'error')
    return state.set(status='failure')
else:
    return state
