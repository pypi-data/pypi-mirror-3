# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from os.path import join

name = "Products.PloneOntology"
path = name.split(".") + ["version.txt"]
version = "1.0.0"

setup(name="Products.PloneOntology",
      version=version,
      description="A discussion board for Plone.",
      long_description=(open("README.txt").read() +
                        open("docs/HISTORY.txt").read()),
      classifiers=[
          "Framework :: Plone",
          "Framework :: Zope2",
          "Programming Language :: Python",
          ],
      keywords="Plone Ontology OWL",
      author="Thomas Förster",
      author_email="plone-developers@lists.sourceforge.net",
      maintainer="Alex Clark",
      maintainer_email="aclark@aclark.net",
      url="https://github.com/collective/Products.PloneOntology",
      license="GPL",
      packages=find_packages(exclude=["ez_setup"]),
      namespace_packages=["Products"],
      include_package_data=True,
      zip_safe=False,
#      download_url="http://plone.org/products/ploneontology",
      install_requires=[
          "setuptools",
          "Products.Relations",
#          "Plone >= 4.0",
          ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
