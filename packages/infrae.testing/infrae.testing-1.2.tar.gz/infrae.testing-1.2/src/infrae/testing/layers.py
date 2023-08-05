# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os.path

from zope.configuration import xmlconfig, config
from zope.testing.cleanup import cleanUp
from zope.component import provideHandler
from zope.site.hooks import setHooks
from zope.component.eventtesting import events
from zope.component.eventtesting import clearEvents as clear_events
from zope.component.eventtesting import getEvents as get_events
from zope.component import getGlobalSiteManager
from grokcore.component import zcml



def get_event_names():
    """Return the names of the triggered events.
    """
    called = map(lambda e: e.__class__.__name__, get_events())
    clear_events()
    return called


class assertTriggersEvents(object):
    """Context manager that check that some events are triggered.
    """

    def __init__(self, *names, **opts):
        self.names = names
        self.msg = opts.get('msg')
        self.triggered = []

    def __enter__(self):
        getGlobalSiteManager().registerHandler(
            self.triggered.append, (None,))

    def __exit__(self, exc_type, exc_val, exc_tb):
        getGlobalSiteManager().unregisterHandler(
            self.triggered.append, (None,))
        if exc_type is None and exc_val is None and exc_tb is None:
            self.verify(map(lambda e: e.__class__.__name__,  self.triggered))

    def verify(self, triggered):
        for name in self.names:
            msg = self.msg
            if msg is None:
                msg = "block didn't trigger event %s, got %s" % (
                    name, ', '.join(triggered))
            assert name in triggered, msg


class assertNotTriggersEvents(assertTriggersEvents):
    """Context manager that check that events are not triggered.
    """

    def verify(self, triggered):
        for name in self.names:
            msg = self.msg
            if msg is None:
                msg = "block triggered event %s, got %s" % (
                    name, ', '.join(triggered))
            assert name not in triggered, msg


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
        clear_events()
        cleanUp()

        # Set up this test layer.
        setHooks()
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
        clear_events()

    def tearDown(self):
        cleanUp()

    def _load_zcml(self, context):
        return xmlconfig.file(
            self.zcml_file,
            package=self.package,
            context=context, execute=True)
