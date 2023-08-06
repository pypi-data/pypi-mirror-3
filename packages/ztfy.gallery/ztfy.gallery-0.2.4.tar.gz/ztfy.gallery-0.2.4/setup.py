### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
This module contains the tool of ztfy.gallery
"""
import os
from setuptools import setup, find_packages

DOCS = os.path.join(os.path.dirname(__file__),
                    'ztfy', 'gallery', 'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')

version = '0.2.4'
long_description = open(README).read() + '\n\n' + open(HISTORY).read()

tests_require = [
    'zope.testing',
]

setup(name='ztfy.gallery',
      version=version,
      description="ZTFY.blog package extension used to handle an images gallery",
      long_description=long_description,
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python",
          "Framework :: Zope3",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='ZTFY Zope3 images gallery',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://www.ztfy.org',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ztfy'],
      include_package_data=True,
      package_data={'': ['*.zcml', '*.txt', '*.pt', '*.pot', '*.po', '*.mo', '*.png', '*.gif', '*.jpeg', '*.jpg', '*.css', '*.js']},
      zip_safe=False,
      # uncomment this to be able to run tests with setup.py
      #test_suite = "ztfy.gallery.tests.test_gallerydocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'fanstatic',
          'hurry.query',
          'z3c.language.switch',
          'zope.annotation',
          'zope.catalog',
          'zope.component',
          'zope.container',
          'zope.interface',
          'zope.intid',
          'zope.location',
          'zope.proxy',
          'zope.publisher',
          'zope.schema',
          'zope.session',
          'zope.traversing',
          'zope.viewlet',
          'zope.app.file',
          'ztfy.blog',
          'ztfy.file',
          'ztfy.skin',
          'ztfy.utils',
          'ztfy.workflow'
      ],
      entry_points={
          'fanstatic.libraries': [
              'ztfy.gallery.back = ztfy.gallery.browser:library',
              'ztfy.gallery.defaultskin = ztfy.gallery.defaultskin:library',
              'ztfy.gallery = ztfy.gallery.skin:library'
          ]
      })
