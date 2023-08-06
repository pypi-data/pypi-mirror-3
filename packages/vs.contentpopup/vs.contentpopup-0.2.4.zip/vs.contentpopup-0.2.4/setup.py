# -*- coding: utf-8 -*-
"""
This module contains the tool of vs.contentpopup
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2.4'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs', 'HISTORY.txt')
    + '\n') 

tests_require = ['zope.testing']

setup(name='vs.contentpopup',
      version=version,
      description="vs.contentpopup",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='Plone overlay popup',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/vs.contentpopup',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vs', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'lxml',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='vs.contentpopup.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
