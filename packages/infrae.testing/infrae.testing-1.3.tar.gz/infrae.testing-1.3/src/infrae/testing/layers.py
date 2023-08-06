# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import os.path

from grokcore.component import zcml
from zope.component import provideHandler
from zope.component.eventtesting import events
from zope.configuration import xmlconfig, config
from zope.site.hooks import setSite, setHooks
import zope.testing.cleanup

from .events import clear_events

class CleanUpCallbacks(object):

    def __init__(self):
        self._callbacks = []

    def add(self, callback):
        self._callbacks.append(callback)

    def __call__(self):
        for callback in self._callbacks:
            callback()

    def clear(self):
        self._callbacks = []


def clear_site():
    setSite(None)
    setHooks()


layerCleanUp = CleanUpCallbacks()
layerCleanUp.add(clear_events)
layerCleanUp.add(zope.testing.cleanup.cleanUp)
testCleanUp = CleanUpCallbacks()
testCleanUp.add(clear_events)
testCleanUp.add(clear_site)


class LayerBase(object):
    """Sane layer base class, for zope.testing layer system.
    """

    __bases__ = ()

    def __init__(self, package, name=None):
        if name is None:
            name = self.__class__.__name__
        self.__name__ = name
        self.__module__ = package.__name__
        self.package = package

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass


class ZCMLLayer(LayerBase):
    """Base layerto load up some ZCML.
    """

    def __init__(self, package, zcml_file='ftesting.zcml', name=None):
        super(ZCMLLayer, self).__init__(package, name)
        self.zcml_file = os.path.join(os.path.dirname(package.__file__),
                                      zcml_file)

    def setUp(self):
        # Previous test layer might be buggy and have left things
        # behind, so clear everything ourselves before doing setup
        # (like ZopeLite)
        layerCleanUp()

        # Set up this test layer.
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        self.context = self._load_zcml(context)
        provideHandler(events.append, (None,))

    def grok(self, module_name):
        try:
            zcml.do_grok(module_name, self.context)
            self.context.execute_actions(testing=True)
        finally:
            del self.context.actions[:]

    def testTearDown(self):
        testCleanUp()

    def tearDown(self):
        layerCleanUp()

    def _load_zcml(self, context):
        return xmlconfig.file(
            self.zcml_file,
            package=self.package,
            context=context, execute=True)
