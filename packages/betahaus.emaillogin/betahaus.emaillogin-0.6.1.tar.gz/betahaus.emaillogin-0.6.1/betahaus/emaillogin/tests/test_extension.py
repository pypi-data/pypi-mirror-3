"""This is an integration "unit" test. It uses PloneTestCase because I'm lazy
"""
from betahaus.emaillogin.interfaces import IEmailPluginExtension


import unittest

from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from Products.Five import zcml
from Products.Five import fiveconfigure

from betahaus.emaillogin.tests import base
from betahaus.emaillogin import email2username

ptc.setupPloneSite()

zcml_string = """\
<configure xmlns="http://namespaces.zope.org/zope"
           package="plone.app.contentrules"
           i18n_domain="plone">

    <utility
        provides="betahaus.emaillogin.interfaces.IEmailPluginExtension"
        component="betahaus.emaillogin.tests.test_extension.dummy_extension"
        permission="zope.Public"
        />
        
</configure>
"""

class DummyExtension(object):
    implements(IEmailPluginExtension)
    
    def getUserNames(self, context, login_email, get_all = False):
        username = login_email.split('@')[0]
        return get_all and [username] or username
    
dummy_extension = DummyExtension()

class TestEmailExtensionLayer(PloneSite):
    
    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        zcml.load_string(zcml_string)
        fiveconfigure.debug_mode = False

    @classmethod
    def tearDown(cls):
        pass
    
class TestEmailExtension(base.TestCase):
    """Test usage of the emaillogin catalog.
    """

    layer = TestEmailExtensionLayer

    def afterSetUp(self):

        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test 
        should be done in that test method.
        """

        self.membership = getToolByName(self.portal, 'portal_membership')



    def beforeTearDown(self):

        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """

    def testSingleUsername(self):
        self.failUnless(email2username(self.portal, 'dummy@email.org') == 'dummy')
        
    def testMultipleUsername(self):
        self.failUnless(email2username(self.portal, 'dummy@email.org', get_all = True) == ['dummy'])
    
           
        

def test_suite():

    """This sets up a test suite that actually runs the tests in the class
    above
    """

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEmailExtension))
    return suite
