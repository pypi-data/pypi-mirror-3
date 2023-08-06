# -*- coding: utf-8 -*-
"""
This module contains the tool of Products.categorynavigator
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.12'

try:
    long_description=read("README.txt") + "\n" + read("docs", "HISTORY.txt")
except:
    long_description=''

tests_require = ['zope.testing']

setup(name='Products.categorynavigator',
      version=version,
      description="Type that permits category based search and navigation on Plone content",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone categories category subject navigation browse tags',
      author='David Jonas',
      author_email='david@v2.nl',
      url='https://svn.v2.nl/plone/Products.categorynavigator',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='Products.categorynavigator.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
