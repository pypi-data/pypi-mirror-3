# -*- coding: utf-8 -*-
# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: setup.py 43650 2010-07-15 14:41:15Z sylvain $

from setuptools import setup, find_packages
import os

version = '1.13'

setup(name='Products.Formulator',
      version=version,
      description="Form library for Zope 2.",
      long_description=open(os.path.join("Products", "Formulator", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "Formulator", "CREDITS.txt")).read() + "\n" +
                       open(os.path.join("Products", "Formulator", "HISTORY.txt")).read(),
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='form generator zope2',
      author='Martijn Faassen and community',
      author_email='info@infrae.com',
      url='http://infrae.com/products/formulator',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
              'setuptools',
              ],
      )
