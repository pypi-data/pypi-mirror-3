from hashlib import sha256
from time import time

from zope import interface
from zope import component
from zope.i18n import translate
from zope.site.hooks import getSite
from zope.publisher.interfaces import IRequest

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from raptus.securelogin import interfaces
from raptus.securelogin import SecureLoginMessageFactory as _

import logging

TOKEN_KEY = 'raptus.securelogin.token'
VALID_KEY = 'raptus.securelogin.valid'


class Secure(object):

    interface.implements(interfaces.ISecure)
    component.adapts(interface.Interface, IRequest)

    def __init__(self, context, request):
        self.request = request
        self.context = getSite()
        self.configuration = interfaces.IConfiguration(getSite())
        self.membership = getToolByName(self.context, 'portal_membership')
        self.registration = getToolByName(self.context, 'portal_registration')
        self.groups = getToolByName(self.context, 'portal_groups')

    def _hash(self, token, seed):
        hash = sha256()
        hash.update(token + seed)
        return hash.digest()

    def enabled(self, username):
        """ Whether secure login is enabled for the provided user
        """
        ip = self.request.get('HTTP_X_FORWARDED_FOR', '')
        if not ip:
            ip = self.request.get('REMOTE_ADDR', '')
        for bypass in self.configuration.ip_bypass:
            if ip.startswith(bypass):
                return False
        for group in self.configuration.groups:
            if username in self.groups.getGroupMembers(group):
                return True
        return False

    def has_token(self, username):
        """ Whether the provided user already received a token
        """
        return int(self.request.SESSION.get(VALID_KEY + '.' + username, 0)) + int(self.configuration.timeout) >= int(time() / 60)

    def check(self, username, token):
        """ Whether the given token is correct for the provided user
        """
        if not self.has_token(username):
            return False
        seed = self.request.SESSION.get(VALID_KEY + '.' + username, '')
        if self._hash(token, seed) == self.request.SESSION.get(TOKEN_KEY + '.' + username, False):
            self.request.SESSION.set(TOKEN_KEY + '.' + username, False)
            self.request.SESSION.set(VALID_KEY + '.' + username, 0)
            return True
        return False

    def send(self, username):
        """ Send a new security token to the provided user
        """
        token = self.registration.getPassword(int(self.configuration.token))
        now = str(int(time() / 60))
        self.request.SESSION.set(TOKEN_KEY + '.' + username, self._hash(token, now))
        self.request.SESSION.set(VALID_KEY + '.' + username, now)
        member = self.membership.getMemberById(username)
        if member is None:
            return
        email = self.configuration.email
        mobile = member.getProperty('mobile', None)
        if email and mobile:
            email = email % dict(number=mobile)
            result = interfaces.SMS
        else:
            email = member.getProperty('email')
            result = interfaces.EMAIL
        mailhost = getToolByName(self.context, 'MailHost')
        if result is interfaces.EMAIL:
            message = translate(_('mail_body',
                                  default='''Use the following token to log in to the site ${site}

    Security token: ${token}

(This token is valid for ${timeout} minutes)''',
                                  mapping={'token': token,
                                           'timeout': self.configuration.timeout,
                                           'site': self.context.getProperty('title')}), context=self.request)
            subject = translate(_('mail_subject',
                                  default='Security token for the site ${site}',
                                  mapping=dict(site=self.context.getProperty('title'))), context=self.request)
        else:
            subject = mobile
            message = token
        email_from_name = self.context.getProperty('email_from_name', '')
        email_from_address = self.context.getProperty('email_from_address', '')
        mailhost.send(message, mto=email, mfrom='%s <%s>' % (email_from_name, email_from_address),
                      subject=subject, charset='utf-8')
        return result
