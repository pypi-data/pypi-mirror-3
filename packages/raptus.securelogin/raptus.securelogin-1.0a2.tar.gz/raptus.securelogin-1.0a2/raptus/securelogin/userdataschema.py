from zope import interface
from zope import schema

from plone.app.users.userdataschema import IUserDataSchemaProvider, IUserDataSchema
from plone.app.users.browser.personalpreferences import UserDataPanelAdapter

from raptus.securelogin import SecureLoginMessageFactory as _


class MobileUserDataSchemaProvider(object):
    interface.implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IMobileUserDataSchema


class IMobileUserDataSchema(IUserDataSchema):
    """ Add a field to enter the mobile phone number used to send the
        security token
    """

    mobile = schema.TextLine(
        title=_(u'Mobile'),
        description=_('description_mobile', default=u'Your mobile phone number able to receive SMS messages.'),
        required=False
    )


class MobileUserDataPanelAdapter(UserDataPanelAdapter):
    interface.implements(IMobileUserDataSchema)

    def get_mobile(self):
        return self._getProperty('mobile')

    def set_mobile(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties({'mobile': value.replace(' ', '').replace('+', '00')})

    mobile = property(get_mobile, set_mobile)
