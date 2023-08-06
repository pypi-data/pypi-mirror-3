## Controller Python Script "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email=''
##title=validates user preferences

from Products.CMFPlone import PloneMessageFactory as _

from betahaus.emaillogin import email2username


member=context.portal_membership.getAuthenticatedMember()
username = member.getId()

def isMemberEmailAllowed(email):
    if len(email) < 1:
        return False
    found_usernames = email2username(context, email, get_all = True)
    
    if username in found_usernames:
        found_usernames.remove(username)
    if not found_usernames:
        return True
    else:
        return False

if not isMemberEmailAllowed(email):
    state.setError('email',
                   _(u'The email you selected is already in use or is not valid. Please use another.'),
                   'email_invalid' )

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')

return state
