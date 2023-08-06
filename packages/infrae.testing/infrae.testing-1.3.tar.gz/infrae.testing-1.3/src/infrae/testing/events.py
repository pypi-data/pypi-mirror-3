# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

from OFS.interfaces import ITraversable

from zope.component import getGlobalSiteManager
from zope.component.eventtesting import clearEvents as clear_events
from zope.component.eventtesting import getEvents as get_events
from zope.component.interfaces import IObjectEvent


def get_event_names(interface=None, object_type=False):
    """Return the names of the triggered events.
    """
    if object_type:

        def display(event):
            name = event.__class__.__name__
            if IObjectEvent.providedBy(event):
                if ITraversable.providedBy(event.object):
                    name += ' for ' + '/'.join(event.object.getPhysicalPath())
            return name

    else:
        display = lambda name: name.__class__.__name__

    called = map(display, get_events(interface))
    clear_events()
    return called


class assertTriggersEvents(object):
    """Context manager that check that some events are triggered.
    """

    def __init__(self, *names, **opts):
        self.names = names
        self.msg = opts.get('msg')
        self.testcase = opts.get('testcase')
        self.triggered = []

    def fail(self, msg):
        if self.testcase is not None:
            self.testcase.fail(msg)
        raise AssertionError(msg)

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
            if name not in triggered:
                self.fail(msg)


class assertNotTriggersEvents(assertTriggersEvents):
    """Context manager that check that events are not triggered.
    """

    def verify(self, triggered):
        for name in self.names:
            msg = self.msg
            if msg is None:
                msg = "block triggered event %s, got %s" % (
                    name, ', '.join(triggered))
            if name in triggered:
                self.fail(msg)

