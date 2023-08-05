# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '0.6.1'

setup(name='monet.mapsviewlet',
      version=version,
      description=("A viewlet for Plone that show up a Google Maps using the document location field. "
                   "Also can handle KML files using related contents."),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: GIS",
        ],
      keywords='plone monet google maps plonegov kml',
      author='Monet',
      author_email='retecivica@comune.modena.it',
      maintainer='RedTurtle Technology',
      maintainer_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/monet.mapsviewlet',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['monet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Maps',
          'archetypes.schemaextender',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
