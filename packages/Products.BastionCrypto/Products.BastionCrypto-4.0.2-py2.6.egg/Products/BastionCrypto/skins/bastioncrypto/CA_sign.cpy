## Controller Python Script "CA_sign"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=keyfile=None,keytext=''
##title=sign a key
##
try:
    context.sign(keyfile, keytext)
except Exception, e:
    context.plone_utils.addPortalMessage(str(e), 'error')
    state.set(status='failure')

return state

