# -*- coding: utf-8 -*-
"""
grape.recipe.pipeline
"""
from setuptools import setup, find_packages

version = '1.1.3'

long_description = ''
entry_point = 'grape.recipe.pipeline:Recipe'
entry_points = {"zc.buildout": [
                  "default = grape.recipe.pipeline:Recipe",
               ]}

setup(name='grape.recipe.pipeline',
      version=version,
      description="grape.recipe.pipeline",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Buildout',
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries :: Python Modules',],
      keywords='grape recipe pipeline',
      author='Maik Roder',
      author_email='roeder@berg.net',
      url='http://big.crg.cat/bioinformatics_and_genomics',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['grape', 'grape.recipe'],
      include_package_data=True,
      zip_safe=False,
      test_suite='grape.recipe.pipeline.tests',
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                        'RestrictedPython',
                        ],
      entry_points=entry_points,
      )
