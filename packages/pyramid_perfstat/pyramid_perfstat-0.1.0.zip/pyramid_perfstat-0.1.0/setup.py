#!/usr/bin/python
# -*- coding: utf-8 -*- 
#-----------------------------------------------------------------------------
# Name:        setup.py
# Purpose:     
#
# Author:      Stéphane Bard
#
# Created:      31 janv. 2012
# Copyright:   -
# Licence:     BSD License
# New field:   ----------
#-----------------------------------------------------------------------------
from setuptools import setup, find_packages
from os.path import join
import sys
import os

long_description ="""Pyramid PerfStat logs and reports statistics
                     about time usage of a pyramid webapp.
                     
                     It acts like a tween and should be rereference
                     in your pyramid .ini file like other tween.
                     
                     after that visit http://localhost:6543/__perfstat/stat
                  """

setup(name='pyramid_perfstat',
      license='BSD License',
      version='0.1.0',
      description='Pyramid PerfStat logs and reports statistics about time usage of a pyramid webapp.',
      long_description=long_description,
      author='Bard Stéphane',
      author_email='stephane.bard@gmail.com',
      url='http://bitbucket.org/tuck/pyramid_perfstat',
      download_url='',
      install_requires=['pyramid>=1.2'],
      packages=find_packages(),
      package_data={'pyramid_perfstat': ['templates/*.mako','static/js/*.js',
                                         'static/images/*.gif',
                                         'static/images/*.css']},
      include_package_data=True,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: User Interfaces',
          'Topic :: Utilities',
      ],
      zip_safe=False,
      entry_points ='',
      )
