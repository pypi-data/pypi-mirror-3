

import os
from setuptools import setup, find_packages

version = '0.7'

setup(name='quintagroup.plonetabs',
      version=version,
      description="Quintagroup Plone Tabs",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='quintagroup plonetabs',
      author='"Quintagroup": http://quintagroup.com/',
      author_email='support@quintagroup.com',
      url='http://quintagroup.com/services/plone-development/products/plone-tabs',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
