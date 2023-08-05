# -*- coding: utf-8 -*-

import zope.schema
import zope.security.interfaces
from zope.container.constraints import contains
from zope.interface import Interface, Attribute, moduleProvides
from dolmen.authentication import MF as _


class IPrincipalFolder(Interface):
    contains('.IPrincipal')

    def hasPrincipal(id):
        """Returns a boolean representing the presence of the
        principal with the given id in the folder.
        """

    def getPrincipal(id):
        """Returns an IPrincipal with the given id.
        """


class IPrincipal(zope.security.interfaces.IGroupAwarePrincipal):
    """Principals are easily identifiable entities that interact
    with the content. Commonly, a principal is a user or a group.
    """
    id = zope.schema.ASCIILine(
        title=_(u'Unique principal identifier.'),
        required=True,
        )

    title = zope.schema.TextLine(
        title=_(u'Principal name'),
        description=_(u'Descriptive name of the principal.'),
        required=True,
        )


class IGroup(zope.security.interfaces.IGroup, IPrincipal):
    """A group of principals.
    """


class IAccountStatus(Interface):
    """An interface managing a simple account status.
    """
    status = Attribute("Status of the account.")

    def check():
        """Returns a boolean. True allows the normal user login.
        False will disable the account and act like a failed login.
        """


class IPasswordChecker(Interface):
    """This interface defines items that can challenge a
    given value against a stored password value.
    """
    def checkPassword(password):
        """Challenges the input password with the stored one.
        Returns True if the passwords match, False otherwise.
        """


class IPasswordProtected(Interface):
    """This interface defines items protected by a password.
    """
    password = zope.schema.Password(
        title=_(u"Password"),
        description=_(u"Enter a password"),
        required=True,
        )


class IAuthenticationInterfaces(Interface):
    """This interface describes and exposes the meaningful interfaces
    of the authentication module.
    """
    IPrincipalFolder = Attribute(
        "A container specialized in storing principal representations.")

    IPrincipal = Attribute(
        "A principal representation, directly inheriting from "
        "zope.security IPrincipal, but redefining several fields "
        "for a user-friendly form display.")

    IGroup = Attribute(
        "A logical grouping of principals. This component is an "
        "IPrincipal itself.")

    IAccountStatus = Attribute(
        "Abstraction component allowing to check the status of a principal.")

    IPasswordChecker = Attribute(
        "Abstraction component in charge of resolving a principal's"
        "credentials.")

    IPasswordProtected = Attribute(
        "This interface defines any component protected by a password")


moduleProvides(IAuthenticationInterfaces)
__all__ = list(IAuthenticationInterfaces)
