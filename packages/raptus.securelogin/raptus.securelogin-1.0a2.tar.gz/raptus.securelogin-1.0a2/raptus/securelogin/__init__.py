from zope.i18nmessageid import MessageFactory

from Products.CMFCore.permissions import ManagePortal
from Products.PluggableAuthService import registerMultiPlugin

SecureLoginMessageFactory = MessageFactory('raptus.securelogin')

from raptus.securelogin import auth


#################################
# register plugins with pas
try:
    registerMultiPlugin(auth.SecureLoginCookieAuthHelper.meta_type)
except RuntimeError:
    # make refresh users happy
    pass


def initialize(context):

    context.registerClass(auth.SecureLoginCookieAuthHelper,
                          permission=ManagePortal,
                          constructors=(auth.manage_addSecureLoginCookieAuthHelperForm,
                                        auth.manage_addSecureLoginCookieAuthHelper),
                          visibility=None
                          )
