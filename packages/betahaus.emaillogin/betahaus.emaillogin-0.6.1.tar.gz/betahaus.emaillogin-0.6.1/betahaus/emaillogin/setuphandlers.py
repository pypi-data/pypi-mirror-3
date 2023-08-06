from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.publisher.interfaces import BadRequest

from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.browser.info import PASInfoView
from Products.Archetypes.utils import shasattr
from betahaus.emaillogin import config

import logging
logger = logging.getLogger(config.PROJECTNAME)

def createEmailLoginPlugin(portal):
    logger.info("Adding a Betahaus plugin, EmailLogin")
    acl=getToolByName(portal, "acl_users")
    
    if not shasattr(acl,'emaillogin'):
        acl.manage_addProduct["betahaus.emaillogin"].addEmailLoginPlugin(id=config.ID, title=config.TITLE)
        logger.info('Added emaillogin plug-in')
    else:
        logger.info("Emaillogin plug-in already exists")


def activatePlugin(portal, plugin_id):
    acl=getToolByName(portal, "acl_users")
    plugin=getattr(acl, plugin_id)
    interfaces=plugin.listInterfaces()

    activate=[]

    for info in acl.plugins.listPluginTypeInfo():
        interface=info["interface"]
        interface_name=info["id"]
        if plugin.testImplements(interface):
            activate.append(interface_name)
            logger.info("Activating interface %s for plugin %s" % \
                    (interface_name, plugin_id))

    plugin.manage_activateInterfaces(activate)
    
def movePluginToTop(portal, plugin_id):
    acl=getToolByName(portal, "acl_users")
    plugin=getattr(acl, plugin_id)
    
    for info in acl.plugins.listPluginTypeInfo():
        interface=info["interface"]
        interface_name=info["id"]
        if plugin.testImplements(interface):
            while acl.plugins.listPlugins(interface) and acl.plugins.listPlugins(interface)[0][0] != plugin_id:
                acl.plugins.movePluginsUp(interface, [plugin_id])


def removePlugin(portal, plugin_id):
    acl=getToolByName(portal, "acl_users")
    if hasattr(acl, plugin_id):
        acl.manage_delObjects(plugin_id)
        logger.info("Removed plugin %s from acl_users." % plugin_id)
        

def findDuplicateEmails(portal):
    acl=getToolByName(portal, "acl_users")
    seen_emails = {}
    duplicates = {}
    
    for user in acl.getUsers():
        user_email = user.getProperty('email')
        if seen_emails.has_key(user_email):
            if not duplicates.has_key(user_email):
                duplicates[user_email] = [seen_emails[user_email]]
            duplicates[user_email].append(user.getId())
        else:
            seen_emails[user_email] = user.getId()
    
    return duplicates
    

def importVarious(context):

    if context.readDataFile('betahaus.emaillogin.various.txt') is None:
        # don't run this step unless the betahaus.emaillogin profile is being
        # applied
        return

    site = context.getSite()
    
    createEmailLoginPlugin(site)
    activatePlugin(site, config.ID)
    movePluginToTop(site, config.ID)
    logger.info('Looking for duplicate email addresses, this might take a while if you have a lot of members.')
    duplicates = findDuplicateEmails(site)
    if duplicates:
        logger.warning("""
            **********************************
            **         DUPLICATE EMAILS     **
            **********************************
            This will cause a problem when using email as login.""")
        for duplicate_email, users_list in duplicates.items():
            logger.warning("""Duplicate email addresses!! 
                              '%s' is registered for users: %s""" % (duplicate_email, users_list))
        
def setupExdended(context):

    if context.readDataFile('betahaus.emaillogin.extended.txt') is None:
        # don't run this step unless the extended profile is being
        # applied
        return

    site = context.getSite()

    email_catalog = getToolByName(site, 'email_catalog', None)
    if email_catalog == None:
        logger.warning('Could not find the email catalog tool.')
        return
    
    if 'email' not in email_catalog.indexes():
        email_catalog.addIndex('email', 'KeywordIndex')
    if 'email' not in email_catalog.schema():
        email_catalog.addColumn('email')
    if 'userid' not in email_catalog.schema():
        email_catalog.addColumn('userid')
    

    logger.info('Building email catalog, this might take a while.')
    email_catalog.clearFindAndRebuild()
    
    
       