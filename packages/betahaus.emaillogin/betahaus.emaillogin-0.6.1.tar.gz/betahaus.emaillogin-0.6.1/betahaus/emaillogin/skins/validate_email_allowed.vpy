## Controller Python Script "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=users=[], resetpassword=[], delete=[]
##title=validates user preferences

from Products.CMFPlone import PloneMessageFactory as pmf

from betahaus.emaillogin import EmailMessageFactory as _
from betahaus.emaillogin import email2username


member = context.portal_membership.getAuthenticatedMember()

def isMemberEmailAllowed(email, member_id):
    if len(email) < 1:
        return False
    names = [name for name in email2username(context, email, get_all=True) if name != member_id and name not in delete]
    if len(names) == 0:
        return True
    return False

# No need to check users that is going to be deleted.
users_to_validate = [user for user in users if user.id not in delete]
for user in users_to_validate:
    if hasattr(user, 'email') and not isMemberEmailAllowed(user.email, user.id):
        msg = _(u'The email you selected is already in use, duplicate emails will break emaillogin for those users. '
                'You might want to consider using another email for user ${userid}',
                mapping={'userid':user.id})

        context.plone_utils.addPortalMessage(msg, 'warning')


return state

