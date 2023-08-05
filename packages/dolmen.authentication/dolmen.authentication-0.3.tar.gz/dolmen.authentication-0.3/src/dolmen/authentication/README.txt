=====================
dolmen.authentication
=====================

Sitting on the top the ``zope.pluggableauth`` package,
``dolmen.authentication`` extends it to add reusable component
descriptions and implementations.

Overview
========

``dolmen.authentication`` provides interfaces and components::

  >>> import dolmen.authentication
  >>> from dolmen.authentication import IAuthenticationInterfaces
  >>> from dolmen.authentication import IAuthenticationEvents
  >>> from dolmen.authentication import IAuthenticationAPI

  >>> IAuthenticationAPI.isOrExtends(IAuthenticationInterfaces)
  True
  
  >>> IAuthenticationAPI.isOrExtends(IAuthenticationEvents)
  True

  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(IAuthenticationAPI, dolmen.authentication)
  True


Descriptive interfaces
======================

``dolmen.authentication`` provides a set of base interfaces that can be
used to normalize an authentication system::

  >>> print IAuthenticationInterfaces.__doc__
  This interface describes and exposes the meaningful interfaces
  of the authentication module.

  >>> interfaceDescription(IAuthenticationInterfaces)
  IPrincipalFolder: A container specialized in storing principal representations.
  IAccountStatus: Abstraction component allowing to check the status of a principal.
  IPrincipal: A principal representation, directly inheriting from zope.security IPrincipal, but redefining several fields for a user-friendly form display.
  IGroup: A logical grouping of principals. This component is an IPrincipal itself.
  IPasswordProtected: This interface defines any component protected by a password
  IPasswordChecker: Abstraction component in charge of resolving a principal'scredentials.

  >>> IAuthenticationInterfaces.providedBy(dolmen.authentication.interfaces)
  True

  >>> verifyObject(IAuthenticationInterfaces, dolmen.authentication.interfaces)
  True


Events interfaces and implementations
=====================================

``dolmen.authentication`` provides a set of basic events that can be
used and declined, in order to handle and trace principals' lifecycles::

  >>> print IAuthenticationEvents.__doc__
  This interface describes and exposes the meaningful events
  descriptions and components of the authentication module.

  >>> interfaceDescription(IAuthenticationEvents)
  IUserLoggedOutEvent: IObjectEvent extending event : a user has logged out.
  IUserLoggedInEvent: IObjectEvent extending event : a user has logged in.
  UserLogoutEvent: An IUserLoggedOutEvent implementation.
  UserLoginEvent: An IUserLoggedInEvent implementation.

  >>> IAuthenticationEvents.providedBy(dolmen.authentication.events)
  True

  >>> verifyObject(IAuthenticationEvents, dolmen.authentication.events)
  True


Principal related components
============================

Finally, ``dolmen.authentication`` provides components that can be used to
interact with ``zope.pluggableauth``.

Locatable PrincipalInfo
-----------------------

If your principal is persisted in a container, it is locatable. The principal
representation (IPrincipalInfo), handled by ``zope.pluggableauth``, could
benefit from the principal location's information.

This is what the LocatablePrincipalInfo component provides::

  >>> from zope.location import ILocation
  >>> from dolmen.authentication import LocatablePrincipalInfo

  >>> 'LocatablePrincipalInfo' in IAuthenticationAPI
  True

  >>> ILocation.implementedBy(LocatablePrincipalInfo)
  True

It can be used to link a user to its own representation in the site or
to any object, like a homefolder or a preferences sheet.

This component is registered an adapter, for the IPrincipal components. Let's
create a persisted principal, to check the behavior::

  >>> from zope.interface import implements

  >>> class User(object):
  ...   implements(dolmen.authentication.IPrincipal)
  ...
  ...   def __init__(self, id, title):
  ...     self.id = id
  ...     self.title = title
  ...     self.description = u"A test user"
  ...     self.groups = []

  >>> myuser = User('Manfred', u"A nice mammoth")

  >>> verifyObject(dolmen.authentication.IPrincipal, myuser)
  True

Currently, `myuser` is not providing ILocation. Adapting it will work,
but the location information will be unexistant::

  >>> from zope.pluggableauth.interfaces import IPrincipalInfo
  >>> adapter = IPrincipalInfo(myuser)

  >>> adapter
  <dolmen.authentication.principal.LocatablePrincipalInfo ...>

  >>> IPrincipalInfo.providedBy(adapter)
  True

  >>> print adapter.__name__
  None
  >>> print adapter.__parent__
  None

Now, if we make the principal a valid ILocation, we can exploit the results::

  >>> from zope.interface import alsoProvides

  >>> class MyParent(object):
  ...   pass

  >>> myuser.__name__ = u"Manfred the mammoth"
  >>> myuser.__parent__ = MyParent()
  >>> alsoProvides(myuser, ILocation)

  >>> adapter = IPrincipalInfo(myuser)

  >>> print adapter.__name__
  Manfred the mammoth
  >>> print adapter.__parent__
  <dolmen.authentication.MyParent object at ...>

Now, the principal info can be resolved into an URL and used as a practical
representation of te principal.
