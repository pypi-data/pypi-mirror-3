from zope import component

from raptus.securelogin import interfaces


def get_secure(context, request):
    return component.getMultiAdapter((context, request), interfaces.ISecure)


def enabled(context, request):
    return get_secure(context, request).enabled()


def check(context, request, token):
    return get_secure(context, request).check(token)


def send(context, request):
    return get_secure(context, request).send()
