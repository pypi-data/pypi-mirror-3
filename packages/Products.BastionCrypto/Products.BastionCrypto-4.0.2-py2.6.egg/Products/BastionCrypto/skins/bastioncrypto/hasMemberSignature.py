## Python Script "hasMemberSignature"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member_id=''
##title=returns if we have your PGP key
##

if member_id:
    member = context.portal_membership.getMemberById(member_id)
else:
    member = context.portal_membership.getAuthenticatedMember()

email = member.email

return email and context.pks.searchResults(mail=email)

