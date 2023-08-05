# -*- coding: utf-8 -*-

from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.interface import implements, Interface, Attribute, moduleProvides


class IUserLoggedInEvent(IObjectEvent):
    """An event trigged when a user logs in.
    """


class IUserLoggedOutEvent(IObjectEvent):
    """An event trigged when a user logs out.
    """


class UserLoginEvent(ObjectEvent):
    """A basic implementation of an IUserLoggedInEvent.
    """
    implements(IUserLoggedInEvent)


class UserLogoutEvent(ObjectEvent):
    """A basic implementation of an IUserLoggedOutEvent.
    """
    implements(IUserLoggedOutEvent)


class IAuthenticationEvents(Interface):
    """This interface describes and exposes the meaningful events
    descriptions and components of the authentication module.
    """
    IUserLoggedInEvent = Attribute(
        "IObjectEvent extending event : a user has logged in.")

    UserLoginEvent = Attribute(
        "An IUserLoggedInEvent implementation.")

    IUserLoggedOutEvent = Attribute(
        "IObjectEvent extending event : a user has logged out.")

    UserLogoutEvent = Attribute(
        "An IUserLoggedOutEvent implementation.")


moduleProvides(IAuthenticationEvents)
__all__ = list(IAuthenticationEvents)
