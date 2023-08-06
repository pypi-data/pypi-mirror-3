#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name          = 'python-safe',
      version       = '0.1.12',
      description   = 'Spatial Analysis F* Engine',
      license       = 'BSD',
      keywords      = 'gis vector feature raster data',
      author        = 'Ole Nielsen',
      author_email  = 'ole.moller.nielsen@gmail.com',
      maintainer        = 'Ariel Núñez',
      maintainer_email  = 'ingenieroariel@gmail.com',
      url   = 'http://github.com/AIFDR/python-safe',
      long_description = read('README'),
      packages = ['safe',
                  'safe.storage',
                  'safe.engine',
                  'safe.impact_functions'],
      package_dir = {'safe': 'safe'},
      package_data = {'safe': ['test/data/*']},
      zip_safe=False,
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
