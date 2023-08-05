# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os
import hashlib
import unittest
import doctest
import difflib

from Acquisition import aq_base
from OFS.interfaces import ITraversable

from zope.component.eventtesting import getEvents
from zope.component.interfaces import IObjectEvent
from zope.configuration.name import resolve

from infrae.testing.xmlindent import XMLSoup


TEST_FACTORIES = {
    '.txt': doctest.DocFileSuite,
    '.py': doctest.DocTestSuite,}


def suite_from_package(package_name, factory):
    """This method looks files in a directory of a package_name and
    create test suite with files contained in it.
    """
    suite = unittest.TestSuite()

    try:
        python_package = resolve(package_name)
    except ImportError:
        raise ValueError("Could not import package %s" % package_name)

    testing_path = os.path.dirname(python_package.__file__)
    for filename in os.listdir(testing_path):
        name, extension = os.path.splitext(filename)
        if extension not in TEST_FACTORIES.keys():
            continue
        if name.endswith('_fixture') or name == '__init__':
            continue

        doc_suite_factory = TEST_FACTORIES[extension]
        default_doc_suite_options = {}
        if doc_suite_factory is doctest.DocFileSuite:
            test_name = os.path.join(testing_path, filename)
            default_doc_suite_options['module_relative'] = False
        else:
            test_name = '.'.join((package_name, name))

        def build_doc_suite(*files, **options):
            options.update(default_doc_suite_options)
            return doc_suite_factory(*files, **options)

        test = factory(build_doc_suite, test_name)
        suite.addTest(test)
    return suite


def repr_event(event):
    """Represent an event as a string.
    """
    str_event = event.__class__.__name__
    if IObjectEvent.providedBy(event):
        if ITraversable.providedBy(event.object):
            str_event += ' for ' + '/'.join(event.object.getPhysicalPath())
    return str_event


class TestCase(unittest.TestCase):
    """Add some usefull assert methods to the default Python TestCase.
    """

    def assertEventsAre(self, expected, interface=None):
        """Asset that trigger events are.
        """
        triggered = map(repr_event, getEvents(interface))
        self.assertItemsEqual(triggered, expected)

    def assertHashEqual(self, first, second, msg=None):
        """Assert the hash values of two strings are the same. It is
        commonly used to compare two large strings.
        """
        hash_first = hashlib.md5(first)
        hash_second = hashlib.md5(second)
        msg = msg or 'string hashes are different.'
        self.assertEquals(hash_first.hexdigest(), hash_second.hexdigest(), msg)

    def assertSame(self, first, second, msg=None):
        """Assert that first is the same same object than second,
        Acquisition wrapper removed. If the condition is not
        satisfied, the test will fail with the given msg if not None.
        """
        if msg is None:
            msg = u'%r is not %r' % (first, second)
        if aq_base(first) is not aq_base(second):
            raise self.failureException(msg)

    def assertStringEqual(self, first, second, msg=None):
        """Assert two string are equals ignore extra white spaces
        around them.
        """
        self.assertEqual(first.strip(), second.strip(), msg)

    def assertXMLEqual(self, xml1, xml2):
        """Assert that two XML content are the same, or fail with a
        comprehensive diff between them.

        You should not use this if you which to compare XML data where
        spaces does matter.
        """
        pretty_xml1 = XMLSoup(xml1.strip()).prettify()
        pretty_xml2 = XMLSoup(xml2.strip()).prettify()
        if pretty_xml1 != pretty_xml2:
            diff = ['XML differ:\n-expected\n+actual\n',] + \
                list(difflib.unified_diff(
                    pretty_xml1.splitlines(True),
                    pretty_xml2.splitlines(True), n=2))[2:]
            raise self.failureException(''.join(diff))
