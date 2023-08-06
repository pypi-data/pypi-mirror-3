## Script (Python) "validate_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##bind state=state
##parameters=userid=None, password=None, password2=None, email=None
##title=Validate password
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as pmf

from betahaus.emaillogin import email2username
from betahaus.emaillogin import EmailMessageFactory as _

found_userid = ''
if email:
    found_userid = email2username(context, email)
    if not found_userid:
        context.plone_utils.addPortalMessage(_("The email address you entered doesn't exist."))

if (found_userid and userid) and (found_userid != userid):
    state.setError('userid', "Email and userid don't match please only specify one.")
    state.setError('email', "Email and userid don't match please only specify one.")

if found_userid and not userid:
    userid = found_userid
    context.REQUEST.set('userid', userid)
    
# Determine if we're checking userids or not
pw_tool = getToolByName(context, 'portal_password_reset')
if not pw_tool.checkUser():
    return state

if not userid and not email:
    state.setError('userid', 'This field is required')
    state.setError('email', 'This field is required')
    
if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
