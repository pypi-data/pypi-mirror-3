# -*- coding: utf-8 -*-

import os, sys
from setuptools import setup, find_packages

version = '1.1'

install_requires = [
    'setuptools',
]

# what I read there seems not working properly for Plone 3.3
# http://plone.org/documentation/manual/upgrade-guide/version/upgrading-plone-4.0-to-4.1/referencemanual-all-pages
if sys.version_info < (2, 6):
    install_requires.append('Plone')
else:
    install_requires.append('Products.CMFPlone')


setup(name='collective.portletpage',
      version=version,
      description="A Plone page that can contain portlets",
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
      keywords='plone portlet content',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      maintainer='RedTurtle Technology',
      maintainer_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.portletpage',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
