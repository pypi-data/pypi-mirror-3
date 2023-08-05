# -*- coding: utf-8 -*-
"""
This module contains the tool of c2.recipe.bkups3
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1b1'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '************************\n'
    + '\n' +
    read('c2', 'recipe', 'bkups3', 'README.txt')
    + '\n' +
    'Contributors\n'
    '***************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '*****************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
   'Download\n'
    '**********\n')

entry_point = 'c2.recipe.bkups3:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require = ['zope.testing', 'zc.buildout']

setup(name='c2.recipe.bkups3',
      version=version,
      description="This recipe is backup for Plone data and send to Amazon S3",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout :: Recipe',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone backup recipe blob s3',
      author='Manabu TERADA',
      author_email='terada@cmscom.jp',
      url='http://www.cmscom.jp',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['c2', 'c2.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                        'boto',
                        'DateTime',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='c2.recipe.bkups3.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
