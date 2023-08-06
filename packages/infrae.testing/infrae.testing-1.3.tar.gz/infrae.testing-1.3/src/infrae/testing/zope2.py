# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import os

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from App.class_init import InitializeClass
from OFS.Application import get_folder_permissions, get_products
from OFS.metaconfigure import get_packages_to_initialize
from OFS.Application import install_product, install_package, AppInitializer
from OFS.Folder import Folder
from Testing import ZopeTestCase
from Testing.makerequest import makerequest
from ZODB.DemoStorage import DemoStorage
from ZODB.FileStorage import FileStorage
from Zope2.App.ClassFactory import ClassFactory
from Zope2.App.startup import TransactionsManager
import AccessControl.User
import App.ZApplication
import OFS.Application
import Products
import ZODB
import transaction

from zope.event import notify
from zope.processlifetime import DatabaseOpened

from .layers import ZCMLLayer
from .events import clear_events

_zope_patched = False


def patch_zope():
    """Patch Zope not to load everything.
    """
    global _zope_patched
    if _zope_patched:
        return

    from App.PersistentExtra import patchPersistent
    patchPersistent()

    # Avoid expensive help registration
    import App.ProductContext
    def null_register_topic(self,id,topic): pass
    App.ProductContext.ProductContext.registerHelpTopic = null_register_topic
    def null_register_title(self,title): pass
    App.ProductContext.ProductContext.registerHelpTitle = null_register_title
    def null_register_help(self,directory='',clear=1,title_re=None): pass
    App.ProductContext.ProductContext.registerHelp = null_register_help

    # Switch off debug mode and set client cache
    import App.config
    config = App.config.getConfiguration()
    config.debug_mode = 0
    config.zeo_client_name = None
    App.config.setConfiguration(config)

    _zope_patched = True


def new_database(base=None, storage=None):
    if storage is None:
        if base is not None:
            storage = DemoStorage(base=base._storage)
        else:
            storage = DemoStorage()
    db = ZODB.DB(storage)
    db.classFactory = ClassFactory
    if base is None:
        notify(DatabaseOpened(db))
    return db


class TestAppInitializer(AppInitializer):
    """Initialize a new (test) application. We don't create any
    default user, and install no products.
    """

    def __init__(self, app, products, packages, users):
        AppInitializer.__init__(self, app)
        self.products = products
        self.packages = packages
        self.users = users
        self.installed_products = []
        self.installed_packages = []

    def install_inituser(self):
        app = self.getApp()
        uf = app.acl_users
        for username, roles in self.users.items():
            uf._doAddUser(username, username, roles, [])

    def install_products(self):
        app = self.getApp()
        for product in self.products:
            self._install_product(product, app)
        for package in self.packages:
            self._install_package(package, app)
        if self.installed_products or self.installed_packages:
            self.commit('Installed test packages.')
            # Installation might have triggered some events. Clear them.
            clear_events()

    def install_tempfolder_and_sdc(self):
        ZopeTestCase.utils.setupCoreSessions(self.getApp())

    def _install_product(self, name, app):
        """Zope 2 install a given product.
        """
        meta_types = []
        if name not in self.installed_products:
            for priority, product_name, index, product_dir in get_products():
                if product_name == name:
                    install_product(app, product_dir, product_name, meta_types,
                                    get_folder_permissions(), raise_exc=1)
                    self.installed_products.append(name)
                    Products.meta_types = Products.meta_types + \
                        tuple(meta_types)
                    InitializeClass(Folder) # WTF ?
                    break

    def _install_package(self, name, app):
        """Zope 2 install a given package.
        """
        if name not in self.installed_packages:
            for module, init_func in get_packages_to_initialize():
                if module.__name__ == name:
                    install_package(app, module, init_func, raise_exc=1)
                    self.installed_packages.append(name)
                    break


class Zope2Layer(ZCMLLayer):
    """Zope 2 app test layer.
    """
    default_products = ['PluginIndexes', 'OFSP', 'PageTemplates']
    default_packages = []
    default_users = {}

    def __init__(self, package, zcml_file='ftesting.zcml',
                 name=None, products=None, packages=None, users=None):
        super(Zope2Layer, self).__init__(package, zcml_file, name)

        # Collect packages, products and users to create/install
        self.products = list(self.default_products)
        if products is not None:
            self.products.extend(products)
        self.packages = list(self.default_packages)
        if packages is not None:
            self.packages.extend(packages)
        self.users = self.default_users.copy()
        if users is not None:
            self.users.update(users)

        # Add to the list to install in Zope the tested package/product
        tested_module = self.__module__
        if tested_module.startswith('Products.'):
            self.products.append(tested_module[9:])
        else:
            self.packages.append(tested_module)

        self._transaction_manager = TransactionsManager()
        self._db = None
        self._test_db = None
        self._test_connection = None
        self._application = None
        self.__logged_in = False

    def setUp(self):
        """Setup a Zope 2 Application.
        """
        patch_zope()

        # Load ZCML
        super(Zope2Layer, self).setUp()

        if 'SETUP_CACHE' in os.environ:
            # Create or use an already existing test data.fs
            filename = os.path.join(os.getcwd(), '%s.%s.fs' % (
                    self.__module__, self.__name__.lower()))
            if os.path.exists(filename):
                self._db = new_database(
                    storage = FileStorage(filename))
                self._reload_zope(self._db)
            else:
                self._db = new_database(
                    storage = FileStorage(filename, create=True))
                self._install_zope(self._db)
        else:
            # Create a in memory database
            self._db = new_database()
            self._install_zope(self._db)

    def _install_zope(self, db):
        """Install a fresh Zope inside the new test DB. Eventually
        install an application afterwards.
        """
        # Create the "application"
        newSecurityManager(None, AccessControl.User.system)
        connection = db.open()
        root = connection.root()
        root['Application'] = OFS.Application.Application()
        app = root['Application']
        # Do a savepoint to get a _p_jar on the application
        transaction.savepoint()

        # Initialize the "application"
        try:
            TestAppInitializer(
                app, self.products, self.packages, self.users).initialize()
            self._install_application(makerequest(
                    app, environ={'SERVER_NAME': 'localhost'}))
        except Exception as error:
            # There was an error during the application 'setUp'. Abort
            # the transaction and continue, otherwise test in other
            # layers might fail because of this failure.
            transaction.abort()
            raise error
        else:
            # Close
            transaction.commit()
        finally:
            # In any case, close the connection and continue
            connection.close()
            noSecurityManager()

    def _reload_zope(self, db):
        """Need to re-mount/re-setup SESSIONs if we just reload a Zope
        instance.
        """
        newSecurityManager(None, AccessControl.User.system)
        connection = db.open()
        root = connection.root()
        assert 'Application' in root, 'Invalid database'
        ZopeTestCase.utils.setupCoreSessions(root['Application'])
        transaction.commit()
        connection.close()
        noSecurityManager()

    def _install_application(self, app):
        """Install more things in the "application".
        """
        pass

    def testSetUp(self):
        super(Zope2Layer, self).testSetUp()

        # Use a simple DemoStorage for the test around the default DB
        self._test_db = self._new_storage(base=self._db)
        self._test_connection = self._test_db.open()
        self._application = App.ZApplication.ZApplicationWrapper(
            self._test_db, 'Application', OFS.Application.Application, ())
        self.get_root_folder().temp_folder.session_data._reset()

    def testTearDown(self):
        # Logout eventually logged in users
        self.logout()

        # Close connection and DB
        transaction.abort()
        self._application = None
        self._test_connection.close()
        self._test_connection = None
        self._test_db = None
        super(Zope2Layer, self).testTearDown()

    def _new_storage(self, base=None):
        """Create a new test storage.
        """
        return new_database(base=base)

    def get_root_folder(self):
        """Return root folder contained in the DB.
        """
        return self._test_connection.root()['Application']

    def get_application(self):
        """Return root folder wrapped inside a test request, which is
        the same object you have when you are working on a real
        published request.
        """
        return makerequest(
            self.get_root_folder(), environ={'SERVER_NAME': 'localhost'})

    def login(self, username):
        """Login with the user called username.
        """
        if self.__logged_in:
            self.logout()
        user_folder = self.get_root_folder().acl_users
        user = user_folder.getUserById(username)
        if user is None:
            raise ValueError("No user %s available" % username)
        newSecurityManager(None, user.__of__(user_folder))
        self.__logged_in = True

    def logout(self):
        """Logout eventually logged in user.
        """
        noSecurityManager()
        self.__logged_in = False
