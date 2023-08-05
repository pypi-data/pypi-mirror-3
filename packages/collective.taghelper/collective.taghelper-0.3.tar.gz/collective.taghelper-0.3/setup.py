# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.taghelper
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.3'

long_description = (
read('README.txt')
        + '\n' +
        'Change history\n'
        '**************\n'
        + '\n' +
        read('CHANGES.txt')
        #+ '\n' +
        #'Detailed Documentation\n'
        #'**********************\n'
        #+ '\n' +
        #read('collective', 'taghelper', 'README.txt')
        #+ '\n' +
        #'Contributors\n'
        #'************\n'
        #+ '\n' +
        #read('CONTRIBUTORS.txt')
        + '\n' +
        'Download\n'
        '********\n')

tests_require = ['zope.testing']

setup(name='collective.taghelper',
      version=version,
      description="""The act of tagging content is tedious and humans will often fail to do it. Taghelper examines the content and extracts the keywords that are most relevant.""",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable'
        ],
      keywords='',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='http://plone.org/products/collective.taghelper/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'yql', 'plone.app.registry',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='collective.taghelper.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      #setup_requires=["PasteScript"],
      #paster_plugins=["ZopeSkel"],
      )
