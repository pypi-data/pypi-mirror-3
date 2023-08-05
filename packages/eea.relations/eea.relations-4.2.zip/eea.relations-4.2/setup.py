""" Installer
"""
from setuptools import setup, find_packages
import os
from os.path import join


NAME = 'eea.relations'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description=("EEA Possible Relations. This package provides a flexible "
                   "way to manage relations in a Plone site. it provides a new "
                   "reference browser widget and a central management "
                   "interface for relations, their labels and requirements."),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords=('eea relations widget reference browser referencebrowserwidget '
                'faceted facetednavigation plone zope python'),
      author='Alin Voinea (eaudeweb), European Environment Agency',
      author_email='webadmin@eea.europa.eu',
      url='http://www.eea.europa.eu/projects/Zope',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pydot',
          'eea.facetednavigation',
          'Products.TALESField',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
