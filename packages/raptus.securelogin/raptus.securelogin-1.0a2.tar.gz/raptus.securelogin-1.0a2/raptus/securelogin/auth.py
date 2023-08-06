from zope import component

from Acquisition import aq_base
from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass

from Products.PlonePAS.plugins.cookie_handler import ExtendedCookieAuthHelper
from Products.PluggableAuthService.interfaces.plugins import IValidationPlugin
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from raptus.securelogin import interfaces
from raptus.securelogin import SecureLoginMessageFactory as _


def manage_addSecureLoginCookieAuthHelper(self, id, title='',
                                          RESPONSE=None, **kw):
    """Create an instance of a secure login cookie auth helper.
    """
    self = self.this()

    o = SecureLoginCookieAuthHelper(id, title, **kw)
    self._setObject(o.getId(), o)
    o = getattr(aq_base(self), id)

    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace?manage_tabs_message=Secure+Login+Authentication+added.')


manage_addSecureLoginCookieAuthHelperForm = PageTemplateFile("zmi/SecureLoginCookieAuthHelperForm", globals())


class SecureLoginCookieAuthHelper(ExtendedCookieAuthHelper):
    meta_type = "Secure Login Authentication"

    security = ClassSecurityInfo()

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """ Extract credentials from cookie or 'request'. """
        login = request.form.get('__ac_name', '')
        if login:
            secure = component.getMultiAdapter((self, request), interfaces.ISecure)
            if not secure.enabled(login):
                return ExtendedCookieAuthHelper.extractCredentials(self, request)
            token = request.form.get('__ac_securitytoken', '')
            if not request.SESSION.get('secureloginenabled', False) or not secure.has_token(login):
                if secure.send(login) is interfaces.EMAIL:
                    msg = _('message_email',
                            default=u'A security token has been sent to your email address, '
                                     'please enter it into the provided field to complete '
                                     'the login.')
                else:
                    msg = _('message_mobile',
                            default=u'A security token has been sent to your mobile number, '
                                     'please enter it into the provided field to complete '
                                     'the login.')
                IStatusMessage(request).add(msg, 'info')
                request.form['secureloginfailure'] = True
                request.SESSION.set('secureloginenabled', True)
                return {}
            if secure.check(login, token):
                request.SESSION.set('secureloginenabled', False)
                return ExtendedCookieAuthHelper.extractCredentials(self, request)
            else:
                request.form['secureloginfailure'] = True
                IStatusMessage(request).add(_('error_token', default=u'The provided security token is not valid.'), 'error')
            return {}
        return ExtendedCookieAuthHelper.extractCredentials(self, request)


InitializeClass(SecureLoginCookieAuthHelper)
