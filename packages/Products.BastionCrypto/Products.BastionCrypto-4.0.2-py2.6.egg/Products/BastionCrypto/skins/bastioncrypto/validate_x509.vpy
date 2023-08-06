## Validator Python Script "validate_x509"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=passphrase1='', passphrase2='', city='', province='', country='', company='',division='', cn='', expires='', size='', output='', pwd1='', pwd2=''
##title=Validates x509 parameters
##
request = context.REQUEST

for param in ('passphrase1', 'passphrase2', 'city', 'province', 'country', 'company', 'division', 'cn', 'expires', 'size'):
    if not request.has_key(param) or request[param] == '':
        state.setError(param, '%s is required' % param)

if len(passphrase1) < 5:
    state.setError('passphrase1', 'Passphrase must be at least 5 characters')
elif passphrase1 != passphrase2:
    state.setError('passphrase1', 'Passwords do not match')
    state.setError('passphrase2', 'Passwords do not match')

if output in ('1', '3'):
    bad = False
    for param in ('pwd1', 'pwd2'):
        if not request.has_key(param) or request[param] == '':
            state.setError(param, '%s is required' % param)
            bad = True
    if not bad and pwd1 != pwd2:
        state.setError('pwd1', 'Passwords do not match')
        state.setError('pwd2', 'Passwords do not match')
    
if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state
