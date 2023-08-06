#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name          = 'python-safe',
      version       = '0.1.7',
      description   = 'Spatial Analysis F* Engine',
      license       = 'BSD',
      keywords      = 'gis vector feature raster data',
      author        = 'Ole Nielsen',
      author_email  = 'ole.moller.nielsen@gmail.com',
      maintainer        = 'Ariel Núñez',
      maintainer_email  = 'ingenieroariel@gmail.com',
      url   = 'http://github.com/AIFDR/python-safe',
      long_description = read('README'),
      packages = ['safe'],
      install_requires  = [],
      tests_require = ['nose'],
      test_suite = 'nose.collector',
      classifiers   = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        ],
)
