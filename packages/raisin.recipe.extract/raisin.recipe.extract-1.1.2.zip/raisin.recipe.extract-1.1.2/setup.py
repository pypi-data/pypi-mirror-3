# -*- coding: utf-8 -*-
"""
raisin.recipe.extract
"""
import os
from setuptools import setup, find_packages

version = '1.1.2'

long_description = """The raisin.recipe.extract package is a Buildout recipe used for
creating the data warehouse of Raisin, the web application used for publishing the
summary statistics of Grape, a pipeline used for processing and analyzing RNA-Seq data.
In ETL terms, it extracts the data to be loaded and transformed into the data
warehouse."""
entry_point = 'raisin.recipe.extract:Recipe'
entry_points = {"zc.buildout": [
                  "default = raisin.recipe.extract:Recipe",
               ]}

setup(name='raisin.recipe.extract',
      version=version,
      description="A Buildout recipe for loading data into the Raisin data warehouse",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Buildout',
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Operating System :: POSIX :: Linux',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: System :: Installation/Setup'],
      keywords='RNA-Seq pipeline ngs transcriptome bioinformatics ETL',
      author='Maik Roder',
      author_email='maikroeder@gmail.com',
      url='http://big.crg.cat/services/grape',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['raisin', 'raisin.recipe'],
      include_package_data=True,
      zip_safe=False,
      test_suite='raisin.recipe.extract.tests',
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                        ],
      entry_points=entry_points,
      )
