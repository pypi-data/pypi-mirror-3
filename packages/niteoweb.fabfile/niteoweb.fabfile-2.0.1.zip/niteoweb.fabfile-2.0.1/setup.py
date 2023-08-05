# -*- coding: utf-8 -*-
"""Installer for this package."""

from setuptools import setup
from setuptools import find_packages

import os


# shamlessly stolen from Hexagon IT guys
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '2.0.1'

setup(name='niteoweb.fabfile',
      version=version,
      description="A bunch of Fabric commands we use all the time.",
      long_description=read('README') +
                       read('docs', 'HISTORY.txt') +
                       read('docs', 'LICENSE.txt'),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='Fabric Python',
      author='NiteoWeb Ltd.',
      author_email='info@niteoweb.com',
      url='http://www.niteoweb.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # list project dependencies
          'Fabric',
          'cuisine',
          'setuptools',
      ],
      )
