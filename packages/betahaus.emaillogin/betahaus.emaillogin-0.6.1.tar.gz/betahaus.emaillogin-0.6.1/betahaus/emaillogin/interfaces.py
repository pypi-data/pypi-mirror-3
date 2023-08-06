from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from zope.interface import Interface


class IEmailCatalog(Interface):
    """Custom catalog for faster emaillookup
    """

class IEmailLoginPlugin(IExtractionPlugin):
    
    def extractCredentials(request):
        """Looks for an email address in __ac_name, 
           finds the first user with that email and ex-changes the email with the username in the request.
           
           Always returns {} to simulate failed extraction this will trigger continued PAS extraction of credentials.  
        """

class IEmailPluginExtension(Interface):
    """Extension to enable custom implementation of username from email adress.
    This is typically meant to be used for content based member implementations
    such as betahaus.memberprofile and Products.remember  
    """
    
    def getUserNames(login_email, get_all = False):
        """returns the username for an email address as a string.
        If the get_all flag is set a list with all usernames for an email adress
        should be returned.
        """