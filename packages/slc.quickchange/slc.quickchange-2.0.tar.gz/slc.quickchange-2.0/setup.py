# -*- coding: utf-8 -*-
"""
This module contains the slc.quickchange package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '2.0'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n')

tests_require = ['zope.testing']

setup(name='slc.quickchange',
      version=version,
      description="A tool that adds Search and Replace functionality for "
      "the content of your objects",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: European Union Public Licence 1.1 "
        "(EUPL 1.1)",
        ],
      keywords='change batch quickchange search replace regex linguaplone',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='https://svn.syslab.com/svn/syslabcom/slc.quickchange/',
      license='GPL + EUPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.LinguaPlone',
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='slc.quickchange.tests.test_docs.test_suite',
      entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
      """,
      )
