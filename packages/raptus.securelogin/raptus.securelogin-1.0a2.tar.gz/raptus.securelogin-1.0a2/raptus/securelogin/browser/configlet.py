from zope import interface
from zope import component
from zope.formlib import form

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase

from plone.app.controlpanel.form import ControlPanelForm

from raptus.securelogin import interfaces
from raptus.securelogin import SecureLoginMessageFactory as _


class SecureLoginControlPanelAdapter(SchemaAdapterBase):

    component.adapts(IPloneSiteRoot)
    interface.implements(interfaces.IConfiguration)

    def __init__(self, context):
        super(SecureLoginControlPanelAdapter, self).__init__(context)
        self.portal = context
        pprop = getToolByName(context, 'portal_properties')
        self.context = pprop.securelogin_properties
        self.encoding = pprop.site_properties.default_charset

    ip_bypass = ProxyFieldProperty(interfaces.IConfiguration['ip_bypass'])
    groups = ProxyFieldProperty(interfaces.IConfiguration['groups'])
    email = ProxyFieldProperty(interfaces.IConfiguration['email'])
    timeout = ProxyFieldProperty(interfaces.IConfiguration['timeout'])
    token = ProxyFieldProperty(interfaces.IConfiguration['token'])


class SecureLoginControlPanel(ControlPanelForm):

    form_fields = form.FormFields(interfaces.IConfiguration)

    label = _(u'Secure login settings')
    description = ''
    form_name = ''
