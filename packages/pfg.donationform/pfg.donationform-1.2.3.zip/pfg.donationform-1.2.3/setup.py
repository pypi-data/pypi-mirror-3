# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.3'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n')

setup(name='pfg.donationform',
      version=version,
      description="A PloneFormGen-based donation form that does checkout via PloneGetPaid.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='ploneformgen donation form getpaid',
      author='David Glick, Groundwire',
      author_email='davidglick@groundwire.org',
      url='http://svn.plone.org/svn/collective/pfg.donationform',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pfg', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'Products.Archetypes',
                        'Products.PloneFormGen',
                        'getpaid.core',
                        'getpaid.formgen>=0.4',
                        'collective.pfg.creditcardfields>=1.2',
                        ],
      extras_require={
          'test': [
              'getpaid.nullpayment>=0.5.0',
              'Products.PloneTestCase',
              'Products.PloneGetPaid>=0.10.4dev',
              'zope.app.intid',
              ],
          },
      test_suite='pfg.donationform.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
