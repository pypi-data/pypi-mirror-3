# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '1.3'

setup(name='infrae.testing',
      version=version,
      description="Define some sane tests layers in Zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva cms zope security',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['infrae',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Zope2',
        'BeautifulSoup',
        'grokcore.component',
        'setuptools',
        'zope.component',
        'zope.configuration',
        'zope.event',
        'zope.processlifetime',
        'zope.site',
        'zope.testing',
        ],
      entry_points = {
        'console_scripts': [
            'xmlindent = infrae.testing.xmlindent:xmlindent',
            ]
        }
      )
