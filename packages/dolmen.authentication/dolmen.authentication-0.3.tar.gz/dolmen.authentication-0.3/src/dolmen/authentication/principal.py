# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.location.interfaces import ILocation
from dolmen.authentication import IPrincipal
from zope.pluggableauth.interfaces import IPrincipalInfo


class LocatablePrincipalInfo(grok.Adapter):
    """A principal info aware of its context location.
    """
    grok.context(IPrincipal)
    grok.implements(ILocation, IPrincipalInfo)
    grok.provides(IPrincipalInfo)

    __name__ = None
    __parent__ = None

    def __init__(self, context):
        self.id = context.id
        self.title = context.title
        self.description = context.description
        self.credentialsPlugin = None
        self.authenticatorPlugin = None
        if ILocation.providedBy(context):
            self.__name__ = context.__name__
            self.__parent__ = context.__parent__
