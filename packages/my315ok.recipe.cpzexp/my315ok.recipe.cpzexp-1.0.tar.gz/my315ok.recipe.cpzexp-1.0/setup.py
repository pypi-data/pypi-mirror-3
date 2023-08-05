# -*- coding: utf-8 -*-
"""
This module contains the tool of my315ok.recipe.cpzexp
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('my315ok', 'recipe', 'cpzexp', 'README.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.txt')
    + '\n' +
   'Download\n'
    '********\n'
    )
entry_point = 'my315ok.recipe.cpzexp:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='my315ok.recipe.cpzexp',
      version=version,
      description="automatic copy zexps to Plone's import directory",
      long_description=long_description,
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='plone import',
      author='adam tang',
      author_email='yuejun.tang@gmail.com',
      url='http://svn.plone.org/svn/collective/',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['my315ok', 'my315ok.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'my315ok.recipe.cpzexp.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
