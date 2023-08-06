from zope.interface import implements
from zope import schema
from zope.component import getUtility
from zope.schema import ValidationError

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.userdataschema import checkEmailAddress as orig_email_check
from plone.app.users.userdataschema import IUserDataSchema as old_Idataschema
from betahaus.emaillogin import email2username


class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IUserDataSchema


class EmailInUseError(ValidationError):
    __doc__ = _('message_email_in_use',
                u"The email address you selected is already in use "
                  "or is not valid as login name. Please choose "
                  "another.")


def checkEmailAddress_email(value):
    orig_email_check(value)
    context = getUtility(ISiteRoot)
    username = email2username(context, value)
    if username and username != context.portal_membership.getAuthenticatedMember().getId():
        raise EmailInUseError
    
    return True


class IUserDataSchema(old_Idataschema):
    """
    """

    email = schema.ASCIILine(
        title=_(u'label_email', default=u'E-mail'),
        description=u'',
        required=True,
        constraint=checkEmailAddress_email)
    
