==============
infrae.testing
==============

``infrae.testing`` defines sanes tests layers for testing in Zope 2, to
use in conjunction with `zope.testing`_.

.. contents::

API
===

It defines:

- A ``ZMLLayer`` which load a ZCML file before your test, and clean
  up after,

- A ``Zope2Layer`` which setup a Zope 2 test instance in a layer.

  You can customize the layer setup to add your tested application
  (like to create a Portal instance).

  If you define the shell environment variable ``SETUP_CACHE`` while
  running the tests, this last setup step will be cached in a
  FileSystem Storage. This makes it reusable between different testing
  sessions, and let you save a considerable amount of time while
  running your tests. Of course don't use the cache if you changed how
  you installed your application.

  By default it provides a environment which is exactly equivalent to
  the one provided by a real running Zope 2 instance (with all VHM,
  session support, temp_folder ...).

  If you compare it to the code of the ``Testing`` module in Zope 2,
  it does the same thing, but it is simpler (and so readable), provides
  an environment which match more a running one and is faster (as you can
  cache the setup operation).

  Every test is run in a separate DemoStorage (installed on top of the
  storage providing the installed application).

- A TestCase base class that provides a bit more of assert methods:

  ``assertHashEqual(s1, s2)``
      Will assert that both md5 hash of the given string are
      equal. This is useful when comparing two large string, and that
      you wish to have readable output error message.

  ``assertSame(a1, a2)``
      Will assert that the first argument *is* the second argument.

  ``assertStringEqual(s1, s2)``
      Will assert that stripped version of both given strings are the same.

  ``assertListEqual(l1, l2)``
      Will assert that both given list contains the same values (equal
      tests) in-depending of the order of those.

  ``assertEventsAre(events, interface=None)``
      Will assert that the triggered events are the ones whose names
      are specified in the given list argument. You can restrict events
      to match to those who implements at least the given interface.

  ``assertXMLEqual(xml1, xml2)``
      Will assert that both given XML strings have the same structure
      and data. The XML strings will be indented and after compared
      between them. In case of differences, the error will only report
      a diff between the indented XML strings.
      Of course don't use this method if you wish to compare two XML
      strings where spaces matters.

      An ``xmlindent`` script can be installed out of this package
      that indent the XML code exactly like the ``assertXMLEqual``
      method does.

- The ``get_event_names`` function will return you the names of the
  events triggered in the layer since *the last time* you called it,
  or the test started.

- Two context managers: ``assertNotTriggersEvents`` and
  ``assertTriggersEvents`` that verify that the given block triggers
  (or not) the given events (specified by their names).

- The ``suite_from_package`` function will construct a
  ``unittest.TestSuite`` out of files found in a package. A ``*.txt``
  file will create ``DocFileSuite``, and a ``*.py`` will create a
  ``DocTestSuite``.


Examples
========

ZCMLLayer
---------

A example to test a package called ``corp.testpackage``. The package
as a ``ftesting.zcml`` file which should mainly load its own
``configure.zcml``::

  import unittest

  from infrae.testing import ZCMLLayer
  import corp.testpackage

  layer = ZCMLLayer(corp.testpackage)


  class MyTestCase(unittest.TestCase):

      layer = layer

The layer provides you a ``grok()`` method that can be used to grok a
module in your test later on.


Zope2Layer
----------

Now our ``corp.testpackage`` is a Zope 2 extension providing some
content. We want to test it installed::

  import unittest

  from infrae.testing import ZCMLLayer
  import corp.testpackage


  class CorpLayer(Zope2Layer):
      """Add some installation tasks to the Zope2Layer.
      """
     default_products = Zope2Layer.default_products + ['CMFCore']
     default_packages = Zope2Layer.default_packages + ['corp.testpackage']
     default_users = Zope2Layer.default_users + {'corp_user': 'CorpRole'}

     def _install_application(self, app):
        factory = app.manage_addProduct['corp.testpackage']
        factory.manage_addCorpPortal('portal')

  layer = CorpLayer(corp.testpackage)


  class MyTestCase(unittest.TestCase):

      layer = layer

      def setUp(self):
          self.root = self.layer.get_application()
          self.layer.login('corp_user')


Of course your ZCML *must* include the ZCML of your package
dependencies. As well we don't recommend to add ``Five`` in the layer
as a ``default_products``, it goes crazy (but include it in your ZCML
!).

The layer provides you the following useful methods:

``login(username)``
   Log as a the given username.

``logout()``
   Logout.

``get_root_folder()``
   Return the root of the database, *not* wrapped in a request.

``get_application()``
   Return the root of the database, wrapped in a request.

Code
====

The code is available through a Mercurial repository at:
https://hg.infrae.com/infrae.testing


.. _zope.testing: http://pypi.python.org/pypi/zope.testing
