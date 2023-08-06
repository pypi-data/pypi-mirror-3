# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os, sys

version = '0.1.0'

setup(name='collective.flowplayerclipviews',
      version=version,
      description="Plugin for Plone and collective.flowplayer. Get statistics on how many times the video has been seen",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Topic :: Multimedia :: Video",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        ],
      keywords='flowplayer video views statistic clip',
      author='keul',
      author_email='luca@keul.it',
      url='http://github.com/keul/collective.flowplayerclipviews',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.flowplayer',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
