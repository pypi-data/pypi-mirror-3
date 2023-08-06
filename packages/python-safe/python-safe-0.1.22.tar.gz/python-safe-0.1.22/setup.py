#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess

from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

MAJOR = 0
MINOR = 1
MICRO = 22
ISRELEASED = True
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = "Unknown"

    return GIT_REVISION

def write_version_py(filename='safe/version.py'):
    cnt = """
# THIS FILE IS GENERATED FROM SAFESETUP.PY
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
git_revision = '%(git_revision)s'
release = %(isrelease)s

if not release:
    version = full_version
"""
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of safe.version messes up the build under Python 3.
    FULLVERSION = VERSION
    if os.path.exists('.git'):
        GIT_REVISION = git_version()
    elif os.path.exists('safe/version.py'):
        # must be a source distribution, use existing version file
        try:
            from safe.version import git_revision as GIT_REVISION
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing " \
                              "safe/version.py and the build directory " \
                              "before building.")
    else:
        GIT_REVISION = "Unknown"

    if not ISRELEASED:
        FULLVERSION += '.dev-' + GIT_REVISION[:7]

    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION,
                       'full_version' : FULLVERSION,
                       'git_revision' : GIT_REVISION,
                       'isrelease': str(ISRELEASED)})
    finally:
        a.close()

    return FULLVERSION


# Creates safe/version.py and returns the full version
full_version = write_version_py()

setup(name          = 'python-safe',
      version       = full_version,
      description   = 'Spatial Analysis Functional Engine',
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
                  'safe.engine.impact_functions_for_testing',
                  'safe.impact_functions'],
      package_dir = {'safe': 'safe'},
      package_data = {'safe': ['test/data/*']},
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
