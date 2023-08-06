"""This is an integration "unit" test. It uses PloneTestCase because I'm lazy
"""


import unittest

from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase import PloneTestCase as ptc

from betahaus.emaillogin.config import ID as plugin_id
ptc.setupPloneSite()


class TestEmaillogin(ptc.PloneTestCase):
    """Test usage of the emaillogin acl plugin.
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
        
        self.acl = getToolByName(self.portal, 'acl_users')




    def beforeTearDown(self):

        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """

    def testExist(self):
        self.failUnless(getattr(self.acl, plugin_id, None))

    def test_position_in_acl(self):
        """Must be at the top
        """
        plugin=getattr(self.acl, plugin_id)
        
        for info in self.acl.plugins.listPluginTypeInfo():
            interface=info["interface"]
            interface_name=info["id"]
            if plugin.testImplements(interface):
                self.assertEquals(self.acl.plugins.listPlugins(interface)[0][0], plugin_id)
                    

        
#    def test_default_use_of_memberpropertyfield(self):
#
#        member = self.membership.getMemberById('user1')
#        member_value = member.getProperty(self.field_id)
#
#        self.assertEquals(self.initial_value, member_value)
#
#        # and now the other way around
#        new_name = 'Buster Keaton'
#        member.setMemberProperties({'fullname':new_name})
#        page = self.folder['user1']
#        content_value = page.schema[self.field_id].get(page)
#        
#        self.assertEquals(content_value, new_name)
#
#
#    def test_memberproperty_creation(self):
#        
#        new_field_id = 'age'
#        member = self.membership.getMemberById('user1')
#        
#        # Assert user doesn't have the property yet
#        self.failIf(member.hasProperty('age'))      
#
#        page = self.folder['user1']
#
#        from archetypes.memberdatastorage.memberpropertyfield \
#            import MemberPropertyField
#        
#        page.schema.addField(MemberPropertyField('age',default='youngster'))
#        page.schema.initializeLayers(page)  # to trigger the field's initializeLayer
#        
#        # re-get the member to pick up the update
#        member = self.membership.getMemberById('user1')
#        
#        # Assert member does have the property now
#        self.failUnless(member.hasProperty('age')) 
#        
#        property_value = member.getProperty('age')
#        content_value  = page.schema['age'].get(page)
#        
#        self.assertEquals(property_value, content_value)
        

    ## TODO: the fallback could be tested more rigorously; 
    ## test properties other than string type

def test_suite():

    """This sets up a test suite that actually runs the tests in the class
    above
    """

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEmaillogin))
    return suite
