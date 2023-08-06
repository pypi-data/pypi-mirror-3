from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.DirectoryView import registerDirectory

from zope.component import getUtility
from zope.i18nmessageid import MessageFactory

from config import globals

from betahaus.emaillogin import config

from plugins import emaillogin
registerMultiPlugin(emaillogin.EmailLogin.meta_type)

EmailMessageFactory = MessageFactory(config.PROJECTNAME)

import logging
logger = logging.getLogger(config.PROJECTNAME)

# Register skins directory
registerDirectory('skins', globals)

def email2username(context, email, get_all=False):
    if context == None:
        context = getUtility(ISiteRoot)
    acl = getToolByName(context, 'acl_users', None)
    if acl and config.ID in acl:
        emailplugin = acl.get(config.ID)
        return emailplugin._get_username_from_email(email, get_all)


def initialize(context):
    from AccessControl import allow_module, allow_class
    
    allow_module('betahaus.emaillogin')
    allow_class(EmailMessageFactory)
    
    context.registerClass(emaillogin.EmailLogin,
                                permission=ManageUsers,
                                constructors=
                                        (emaillogin.manage_addEmailLoginPlugin,
                                        emaillogin.addEmailLoginPlugin),
                                visibility=None,
                                icon="www/email.png")

    def reindex_after(func):
        logger.info('Adding reindex-after wrapper for custom email catalog to %s.%s' % (func.__module__, func.__name__))
        def indexer(*args, **kwargs):
            context = args[0]
            value = func(*args, **kwargs)
            try: context.email_catalog.reindexObject(context.portal_membership.getMemberById(context.getId()))
            except: pass
            return value
        return indexer
    
    # These two monky patches could probably be done in a better way, that does not need patching.
    # maybe some kind of subscriber when the user preferences are updated?
    # If anyone looking at this know of a way to catch when a users properties has changed, 
    # please let me know! ;) 
    from Products.PlonePAS.plugins.ufactory import PloneUser
    PloneUser.setProperties = reindex_after(PloneUser.setProperties)

    from Products.CMFCore.MemberDataTool import MemberData    
    MemberData.notifyModified = reindex_after(MemberData.notifyModified)

    def delete_indexer(func):
        logger.info('Adding delete indexer wrapper for custom email catalog to Products.CMFCore.MembershipTool.MembershipTool.deleteMembers')
        def indexer(*args, **kwargs):
            context = args[0]
            if len(args) > 1:
                users = args[1]
                for user in users:
                    try: context.email_catalog.unindexObject(context.portal_membership.getMemberById(user))
                    except: pass
            return func(*args, **kwargs)
        return indexer
    
    from Products.CMFCore.MembershipTool import MembershipTool
    MembershipTool.deleteMembers = delete_indexer(MembershipTool.deleteMembers)
    
