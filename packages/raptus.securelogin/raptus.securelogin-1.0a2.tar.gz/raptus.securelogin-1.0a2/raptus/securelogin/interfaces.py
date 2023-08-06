# -*- coding: utf-8 -*-
from zope import interface
from zope import schema

from raptus.securelogin import SecureLoginMessageFactory as _

EMAIL = object()
SMS = object()


class InvalidEmailAddress(schema.ValidationError):
    __doc__ = _('error_pattern', default=u'Email pattern has to contain «%(number)s»')


def validateEmail(value):
    if not '%(number)s' in value:
        raise InvalidEmailAddress(value)
    return True


class IConfiguration(interface.Interface):

    ip_bypass = schema.List(
        title=_(u'IP'),
        description=_('description_ip_bypass', default=u'IPs for which to bypass the secure login procedure.'),
        required=False,
        value_type=schema.TextLine()
    )

    groups = schema.Set(
        title=_(u'Groups'),
        description=_('description_groups', default=u'Groups for which to enforce the secure login procedure.'),
        value_type=schema.Choice(
            source='plone.app.vocabularies.Groups',
        ),
        required=False
    )

    email = schema.TextLine(
        title=_(u'Email pattern'),
        description=_('description_email', default=u'The email address (has to contain «%(number)s», which will '
                      'be replaced by the mobile phone number of the user) to send '
                      'the security token to. If omitted the security token will be '
                      'sent to the email address of the user.'),
        required=False,
        constraint=validateEmail
    )

    timeout = schema.Int(
        title=_(u'Validity'),
        description=_('description_timeout', default=u'Number of minutes a security token is valid.'),
        default=5,
        required=True
    )

    token = schema.Int(
        title=_(u'Token length'),
        description=_('description_token', default=u'Length of the generated security token.'),
        default=8,
        required=True
    )


class ISecure(interface.Interface):

    def enabled(username):
        """ Whether secure login is enabled for the provided user
        """

    def has_token(username):
        """ Whether the provided user already received a token
        """

    def check(username, token):
        """ Whether the given token is correct for the provided user
        """

    def send(username):
        """ Send a new security token to the provided user
        """
