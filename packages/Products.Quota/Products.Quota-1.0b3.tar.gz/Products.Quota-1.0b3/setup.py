# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os


def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()

version = '1.0b3'

setup(name='Products.Quota',
      version=version,
      description="Adds a folder type with a size limit to your Plone site.",
      long_description="\n".join([
          read("README.txt"),
          read("docs", "TODO.txt"),
          read("docs", "HISTORY.txt"),
      ]),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone quota',
      author='Enrique Peréz',
      author_email='eperez@yaco.es',
      url='http://plone.org/products/quota',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
