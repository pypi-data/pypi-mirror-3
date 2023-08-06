## Controller Python Script "pgp_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=keyfile='',keytext=''
##title=add your PGP Key
##
try:
    context.add(keyfile, keytext)
except Exception, e:
    context.plone_utils.addPortalMessage(str(e), 'error')
    state.set(status='failure')

return state

