## Script (Python) "mail_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Mail a user's password
##parameters=

from Products.CMFPlone import PloneMessageFactory as pmf

from betahaus.emaillogin import email2username
from betahaus.emaillogin import EmailMessageFactory as _

REQUEST=context.REQUEST


email = REQUEST.get('email', None)
if email:
    found_username = email2username(context, email)
    if found_username:
        REQUEST.set('userid', found_username)
    else:
        context.plone_utils.addPortalMessage(pmf("Invalid email address."))
        response = context.mail_password_form()
        

userid = REQUEST.get('userid', '')
if userid != '':
    try:
        response = context.portal_registration.mailPassword(REQUEST['userid'], REQUEST)
    except ValueError, e:
        context.plone_utils.addPortalMessage(pmf(str(e)))
        response = context.mail_password_form()
else:
    context.plone_utils.addPortalMessage(_("Username not found. Remember that usernames are case sensitive."))
    response = context.mail_password_form()

return response
