# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = open(os.path.join("sc", "psc", "policy",
                            "version.txt")).read().strip()

setup(name='sc.psc.policy',
      version=version,
      description="A site policy intended to deploy a package repository like \
                   PyPi or plone.org/downloads, using Plone Software Center",
      long_description=open(os.path.join("sc", "psc", "policy",
                                         "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='psc plone package catalog',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='https://bitbucket.org/simplesconsultoria/sc.psc.policy',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sc', 'sc.psc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.PloneSoftwareCenter',
          'collective.psc.blobstorage==0.1.1',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
