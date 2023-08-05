# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.5.2'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

setup(name='collective.salesforce.authplugin',
      version=version,
      description="Zope PAS plugin providing authentication against objects in Salesforce",
      long_description=long_description,
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='Zope CMF Plone Salesforce.com CRM PAS authentication',
      author='Plone/Salesforce Integration Group',
      author_email='plonesf@googlegroups.com',
      url='http://groups.google.com/group/plonesf',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.salesforce'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'beatbox>=16.0dev',
          'Products.salesforcebaseconnector>=1.2b1',
      ],
      )
