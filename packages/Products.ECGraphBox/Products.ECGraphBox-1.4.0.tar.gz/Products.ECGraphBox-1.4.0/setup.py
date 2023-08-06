# -*- coding: utf-8 -*-
#
# $Id: setup.py 1249 2009-09-23 20:54:12Z amelung $

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('Products', 'ECGraphBox', 'version.txt').strip()
readme  = read('Products', 'ECGraphBox', 'README.txt')
history = read('Products', 'ECGraphBox', 'CHANGES.txt')

long_description = readme + '\n\n' + history

setup(name='Products.ECGraphBox',
      version=version,
      description = "ECGraphBox is a product especially designed for graph assignments.",
      long_description = long_description,

      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords = '',
      author = 'Gino Gulamhussene and Fabian Fett', 
      author_email = 'ginogulamhussene@gmx.de and fett@st.ovgu.de',
      url = 'http://plone.org/products/ecgraphbox/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.ECAssignmentBox >= 1.5',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
