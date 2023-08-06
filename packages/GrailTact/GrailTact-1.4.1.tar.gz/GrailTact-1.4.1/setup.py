# -*- coding: utf-8 -*-
"""
This module contains the tool of GrailTact
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.4.1'

long_description = (
    open(os.path.join("GrailTact", "GrailTact", "readme.txt")).read() +'\n\n' +\
    open(os.path.join("GrailTact", "GrailTact", "changes.txt")).read()
)

tests_require = ['zope.testing']

setup(name='GrailTact',
      version=version,
      description="Contact database with good import/export (general connectivity)",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='Morten W. Petersen',
      author_email='morten@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['GrailTact', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'MegamanicEdit>=1.4.1',
                        'VariousDisplayWidgets'
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='GrailTact.GrailTact.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
