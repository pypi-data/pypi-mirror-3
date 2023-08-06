# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import os
import hashlib
import unittest
import doctest
import difflib

from Acquisition import aq_base
from zope.configuration.name import resolve

from infrae.testing.xmlindent import XMLSoup

from . import events, testmethods


TEST_FACTORIES = {
    '.txt': doctest.DocFileSuite,
    '.py': doctest.DocTestSuite,}
TEST_OPTIONS = {
    '.txt': {'module_relative': False}}


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

        suite_factory = TEST_FACTORIES[extension]
        suite_options = {}
        suite_options.update(TEST_OPTIONS.get(extension, {}))
        if suite_factory is doctest.DocTestSuite:
            test_name = '.'.join((package_name, name))
        else:
            test_name = os.path.join(testing_path, filename)

        def build_suite(*files, **options):
            options.update(suite_options)
            return suite_factory(*files, **options)

        test = factory(build_suite, test_name)
        suite.addTest(test)
    return suite


class ZopeTestMethods(object):

    def assertTriggersEvents(self, msg=None, *expected):
        """Verify that some events are triggered.
        """
        return events.assertTriggersEvents(
            *expected, msg=None, testcase=self)

    def assertNotTriggersEvents(self, msg=None, *expected):
        """Verify that some events are not triggered.
        """
        return events.assertNotTriggersEvents(
            *expected, msg=None, testcase=self)

    def assertEventsAre(self, expected, interface=None):
        """Asset that trigger events are.
        """
        self.assertItemsEqual(
            events.get_event_names(interface=interface, object_type=True),
            expected)

    def assertHashEqual(self, first, second, msg=None):
        """Assert the hash values of two strings are the same. It is
        commonly used to compare two large strings.
        """
        hash_first = hashlib.md5(first)
        hash_second = hashlib.md5(second)
        msg = msg or 'string hashes are different.'
        self.assertEqual(hash_first.hexdigest(), hash_second.hexdigest(), msg)

    def assertContentEqual(self, first, second, msg=None):
        """Assert that first is the same same object than second,
        Acquisition wrapper removed. If the condition is not
        satisfied, the test will fail with the given msg if not None.
        """
        if msg is None:
            msg = u'%r is not %r' % (first, second)
        if aq_base(first) is not aq_base(second):
            raise self.fail(msg)

    def assertContentItemsEqual(self, first, second, msg=None):
        """Assert that a sequence of content equals a second one.
        """
        # Using directly assertItemsEqual, except under Linux ...
        self.assertSequenceEqual(
            sorted(first, key=lambda c: c._p_oid),
            sorted(second, key=lambda c: c._p_oid),
            msg=msg)

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
            raise self.fail(''.join(diff))


class TestMethods(ZopeTestMethods, testmethods.TestMethods):
    """TestCase assert methods that can be used without a TestCase.
    """


class TestCase(ZopeTestMethods, unittest.TestCase):
    """Add some usefull assert methods to the default Python TestCase,
    to test Zope related code.
    """

