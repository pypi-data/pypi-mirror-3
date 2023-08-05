# -*- coding: utf-8 -*-
"""
This module contains the tool of c2.recipe.bitbucketbk
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0b1'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('c2', 'recipe', 'bitbucketbk', 'README.txt')
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
    '********\n')

entry_point = 'c2.recipe.bitbucketbk:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require = ['zope.testing', 'zc.buildout']

setup(name='c2.recipe.bitbucketbk',
      version=version,
      description="This package is backupp repository from bitbucket.org",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='bitbucket backup',
      author='Manabu TERADA',
      author_email='terada@cmscom.jp',
      url='http://www.cmscom.jp',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['c2', 'c2.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='c2.recipe.bitbucketbk.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
