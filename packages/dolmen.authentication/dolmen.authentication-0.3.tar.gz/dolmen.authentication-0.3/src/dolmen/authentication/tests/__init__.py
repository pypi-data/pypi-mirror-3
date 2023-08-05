#-*- coding: utf-8 -*-

import zope.component
from zope.component.testlayer import ZCMLFileLayer
from zope.interface import Interface


class DolmenAuthentication(ZCMLFileLayer):

    def setUp(self):
        ZCMLFileLayer.setUp(self)
        zope.component.hooks.setHooks()
 
    def tearDown(self):
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()
        ZCMLFileLayer.tearDown(self)
