# -*- coding: utf-8 -*-
"""
This module contains the tool of getpaid.pfgbuyableadapter
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0.2'

long_description = (
    read('README.md')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('getpaid', 'pfgbuyableadapter', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n')

tests_require = ['zope.testing']

setup(name='getpaid.pfgbuyableadapter',
      version=version,
      description="An adapter for PloneFormGen to allow forms to be purchased.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='Anderson Leeb Inc',
      author_email='admin@andersonleeb.com',
      url='http://github.com/ianderso/getpaid.pfgbuyableadapter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['getpaid', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'Products.PloneFormGen',
                        'Products.PloneGetPaid',
                        'mysql-python',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='getpaid.pfgbuyableadapter.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
