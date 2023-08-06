# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='jalon.edit',
      version=version,
      description="Installation de JalonEdit",
      long_description=open("README.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Bordonado Christophe - Université Nice Sophia Antipolis (uns) Service TICE',
      author_email='tice@unice.Fr',
      url='http://unice.fr',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jalon'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.quickupload',
          'Products.Collage',
          'collective.fancybox',
          'jalonedit.theme',
          'jalonedit.content',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
