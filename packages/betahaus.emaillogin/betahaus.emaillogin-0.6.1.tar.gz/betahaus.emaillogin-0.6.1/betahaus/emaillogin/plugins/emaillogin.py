from zope.interface import implements

from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from betahaus.emaillogin.interfaces import IEmailLoginPlugin, IEmailPluginExtension
from betahaus.emaillogin.config import CATALOG_ID
from zope.component._api import queryUtility

manage_addEmailLoginPlugin = PageTemplateFile("../www/emailloginAdd", globals(), 
                __name__="manage_addEmailLoginPlugin")

def addEmailLoginPlugin(self, id, title='', REQUEST=None):
    """Add a EmailLogin plugin to a Pluggable Authentication Service.
    """
    p=EmailLogin(id, title)
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=EmailLogin+plugin+added." %
                self.absolute_url())


# For LDAPUserFolder, if 'email' is mapped to an attribute, then it will 
# search by the attribute instead, which makes life easy for us
_DEFAULT_MAIL_PROPS = ('email',)


class EmailLogin(BasePlugin):
    
    meta_type = "EmailLogin plugin"
    security  = ClassSecurityInfo()
    implements(IEmailLoginPlugin)
    
    def __init__(self, id, title=None):

        self._id = self.id = id
        self.title = title


    def _get_username_from_email(self, login_email, get_all = False):
        """Returns the username for a given email. If no user found it returns None"""
        extension = queryUtility(IEmailPluginExtension)
        if extension is not None:
            return extension.getUserNames(self, login_email, get_all = get_all)
            
        email_catalog = getToolByName(self, CATALOG_ID, None)
        if email_catalog != None:
            user = email_catalog(email=login_email)
            if get_all:
                return [x.userid for x in user]
            if len(user) == 1:
                return user[0].userid
        else:
            emails = []
            pas = self._getPAS()
            mail_props = self.getProperty('mail_props', _DEFAULT_MAIL_PROPS)
            for mail_key in mail_props:
                query = {mail_key: login_email, "exact_match": True}
                for user in pas.searchUsers(**query):
                    if not get_all:
                        return user['login']
                    emails.append(user['login'])
            return emails
        return None


    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        login_email = request.get("__ac_name", '').strip()
    
        if login_email == '' or '@' not in login_email:
            return {}
        
        login_name = self._get_username_from_email(login_email)
        if login_name is not None:
            request.set("__ac_name", login_name)
            password=request.get("__ac_password", None)
            return { "login" : login_name, "password" : password }
        return {}
    
    
classImplements(EmailLogin, IExtractionPlugin)
