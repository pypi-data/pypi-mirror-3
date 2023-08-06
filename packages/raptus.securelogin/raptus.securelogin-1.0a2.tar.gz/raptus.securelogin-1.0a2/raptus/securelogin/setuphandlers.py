from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.Extensions.Install import setupAuthPlugins, activatePluginInterfaces

from raptus.securelogin import auth

PROPERTIES = (
    ('ip_bypass', 'lines', ''),
    ('groups', 'lines', ''),
    ('email', 'string', ''),
    ('timeout', 'int', 5),
    ('token', 'int', 8)
)

PLUGIN_ID = 'secureloginauth'


def setupVarious(context):
    if context.readDataFile('raptus.securelogin_various.txt') is None:
        return

    portal = context.getSite()

    properties = getToolByName(portal, 'portal_properties').securelogin_properties
    for id, type, default in PROPERTIES:
        if not properties.hasProperty(id):
            properties._setProperty(id, default, type)

    acl = getToolByName(portal, 'acl_users')

    if acl.objectIds(['Extended Cookie Auth Helper']):
        disable=['IExtractionPlugin', 'ICredentialsResetPlugin', 'ICredentialsUpdatePlugin']
        activatePluginInterfaces(portal, 'credentials_cookie_auth',
                disable=disable)
    if not acl.objectIds(['Secure Login Authentication']):
        auth.manage_addSecureLoginCookieAuthHelper(acl, 'securelogin_credentials_cookie_auth', cookie_name='__ac')
        disable=['ICredentialsResetPlugin', 'ICredentialsUpdatePlugin', 'IChallengePlugin']
        activatePluginInterfaces(portal, 'securelogin_credentials_cookie_auth',
                disable=disable)


def uninstallVarious(context):
    if context.readDataFile('raptus.securelogin_uninstall.txt') is None:
        return

    portal = context.getSite()

    cp = getToolByName(portal, 'portal_controlpanel')
    if 'SecureLoginSettings' in cp:
        cp.unregisterConfiglet('SecureLoginSettings')

    acl = getToolByName(portal, 'acl_users')

    if acl.objectIds(['Secure Login Authentication']):
        acl.manage_delObjects(['securelogin_credentials_cookie_auth'])

    disable=['ICredentialsResetPlugin', 'ICredentialsUpdatePlugin']
    activatePluginInterfaces(portal, 'credentials_cookie_auth',
            disable=disable)
