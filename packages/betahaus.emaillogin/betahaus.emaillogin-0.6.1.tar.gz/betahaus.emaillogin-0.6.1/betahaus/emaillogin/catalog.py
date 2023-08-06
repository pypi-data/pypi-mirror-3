"""We use our own catalog for member data"""

from zope import interface
from zope.interface import implements

from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import manage_zcatalog_entries as ManageZCatalogEntries
from AccessControl.Permissions import search_zcatalog as SearchZCatalog

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable

from betahaus.emaillogin.config import CATALOG_ID
from betahaus.emaillogin.interfaces import IEmailCatalog

class MemberCatalogWrapper(object):
    """This is to fake that the members are in a folder.
    
    The catalog expects to get a folderish object that by using 'objectItems' will return the list of objects.
    """
    
    def __init__(self, objects):
        self.objects = objects
        
    def objectItems(self):
        """objectItems should return a list of tuples like ('id_of_the_object', the_object) """
        return ((obj.id, obj) for obj in self.objects)

class EmailCatalog(CatalogTool):
    id = CATALOG_ID
    security = ClassSecurityInfo()
    
    implements(IEmailCatalog)


    security.declareProtected(ManageZCatalogEntries, 'clearFindAndRebuild')
    def clearFindAndRebuild(self):
        """Empties catalog, then reindexes all the members by asking the portal_membership to list its users.
           
           This can take a long time if there are a lot of users.
        """
        def emailIndexObject(obj, path):
            getToolByName(obj, 'email_catalog').indexObject(obj)

        self.manage_catalogClear()
        members = MemberCatalogWrapper(self.portal_membership.listMembers())
        self.ZopeFindAndApply(members, search_sub=True, apply_func=emailIndexObject)

    def reindexObject(self, object, idxs=[]):
        # this is to get the Catalog to recognize the email and username.
        # Cannot use id as metadata since the id becomes the catalog.
        object.userid = object.id
        object.email = object.getProperty('email')
        super(EmailCatalog, self).reindexObject(object, idxs)
        
    indexObject = reindexObject


    def resolve_path(self, path):
        """
        Attempt to resolve a url into an object in the Zope
        namespace. The url may be absolute or a catalog path
        style url. If no object is found, None is returned.
        No exceptions are raised.
        """
        try: return self.portal_membership.getMemberById(path.split('/')[-1])
        except: pass
        
