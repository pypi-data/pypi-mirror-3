# -*- coding: utf-8 -*-

from zope.interface import moduleProvides, Attribute

from zope.i18nmessageid import MessageFactory
MF = MessageFactory('dolmen.authentication')

from dolmen.authentication.interfaces import *
from dolmen.authentication.interfaces import IAuthenticationInterfaces

from dolmen.authentication.events import *
from dolmen.authentication.events import IAuthenticationEvents

from dolmen.authentication.principal import LocatablePrincipalInfo


class IAuthenticationAPI(IAuthenticationInterfaces, IAuthenticationEvents):
    """The dolmen authentication public components.
    """
    LocatablePrincipalInfo = Attribute(
        "A zope.pluggableauth IPrincipalInfo implementation providing "
        "an information about the principal location, if the principal "
        "is located within the site")


moduleProvides(IAuthenticationAPI)
__all__ = list(IAuthenticationAPI)
