# -*- coding: utf-8 -*-
"""
This module contains the editonpro integration layer
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '==============\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '======================\n'
    + '\n' +
    read('slc', 'editonpro', 'README.txt')
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    )

tests_require=['zope.testing']


setup(name='slc.editonpro',
      version=version,
      description="Integration layer for Edit On Pro Webeditor",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)",
        ],
      keywords='plone wysiwyg editor editonpro',
      author='Syslabcom GmbH',
      author_email='info@syslab.com',
      url='https://svn.plone.org/svn/collective/slc.editonpro',
      license='GPL + EUPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'PasteScript',
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'slc.editonpro.tests.test_docs.test_suite',
      entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
      """,
      paster_plugins = ["ZopeSkel"],
      )

