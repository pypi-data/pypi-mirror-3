## Python Script "getSignatoryInfo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=gathers info about signatories of SignedDocument's
##

results = []
key_server = context.pks
key_server_url = key_server.absolute_url()

# get key server brains ...
infos = key_server.searchResults(id=context.signatoryIds())

# add in absolute_url ...
for brain in infos:
    results.append({'id':brain['id'],
                    'email':brain['email'],
		    'comment':brain['comment'],
		    'name': brain['name'],
		    'date': filter(lambda x,y=brain['id']: x[0] == y, context.signatories)[0][1],
		    'absolute_url':'%s/%s' % (key_server_url, brain['id'])})

return results
