"""This is an integration "unit" test. It uses PloneTestCase because I'm lazy
"""


import unittest

from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase import PloneTestCase as ptc

from betahaus.emaillogin.config import CATALOG_ID
from betahaus.emaillogin.tests import base
ptc.setupPloneSite()


class TestEmailCatalog(base.TestCase):
    """Test usage of the emaillogin catalog.
    """

    def afterSetUp(self):

        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test 
        should be done in that test method.
        """

        self.membership = getToolByName(self.portal, 'portal_membership')

        # create our own member to mess with
        self.membership.addMember('user1', 'u1', ['Member'], [],
                                  {'email': 'user1@host.com',
                                   'fullname': 'User 1'})
        
        setup = getToolByName(self.portal, 'portal_setup')
        setup.runAllImportStepsFromProfile("profile-betahaus.emaillogin:exdended", purge_old=False)
        
        self.email_catalog = getToolByName(self.portal, 'email_catalog')




    def beforeTearDown(self):

        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """

    def testCatalogExist(self):
        self.failUnless(getattr(self.portal, CATALOG_ID, None))
        
    def testCatalogIndexes(self):
        indexes = self.email_catalog.indexes()
        self.assertEquals(indexes, ['email'])        

    def testCatalogColumns(self):
        columns = self.email_catalog.schema()
        self.assertEquals(len(columns), 2)
        self.failUnless('email' in columns)
        self.failUnless('userid' in columns)
        
    def testSearch(self):
        user = self.email_catalog(email = 'user1@host.com')
        self.failUnless(len(user) == 1)
        self.assertEquals(user[0].userid, 'user1')
    
    def testClearAndRebuild(self):
        self.email_catalog.manage_catalogClear()
        self.assertEquals(self.email_catalog.uniqueValuesFor('email'), ())
        self.email_catalog.clearFindAndRebuild()
        self.assertEquals(self.email_catalog.uniqueValuesFor('email'), ('user1@host.com',))
        
    def testCatalogRemovedOnUnistall(self):
        self.portal.portal_quickinstaller.uninstallProducts(['betahaus.emaillogin'])
        self.failIf(getattr(self.portal, CATALOG_ID, None))
        self.portal.portal_quickinstaller.installProducts(['betahaus.emaillogin'])        
        

def test_suite():

    """This sets up a test suite that actually runs the tests in the class
    above
    """

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEmailCatalog))
    return suite
