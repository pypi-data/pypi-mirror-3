from betahaus.emaillogin.setuphandlers import removePlugin
from betahaus.emaillogin import config


def uninstall(portal):
    removePlugin(portal, config.ID)