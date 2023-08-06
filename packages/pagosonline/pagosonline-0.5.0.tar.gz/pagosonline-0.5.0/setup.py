#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

MAJOR = 0
MINOR = 5
MICRO = 0
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

def write_version_py(filename='pagosonline/version.py'):
    cnt = """# THIS FILE IS GENERATED FROM setup.py in pagosonline
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
git_revision = '%(git_revision)s'
release = %(isrelease)s

if not release:
    version = full_version
"""
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of pagosonline.version messes up the build under Python 3.
    FULLVERSION = VERSION
    if os.path.exists('.git'):
        GIT_REVISION = git_version()
    elif os.path.exists('pagosonline/version.py'):
        # must be a source distribution, use existing version file
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


# Creates pagosonline/version.py and returns the full version
full_version = write_version_py()

setup(name          = 'pagosonline',
      version       = full_version,
      description   = 'Satchmo gateway for the Colombian pagosonline service',
      license       = 'BSD',
      keywords      = 'satchmo pagosonline',
      author        = 'Mauricio Mercado',
      author_email  = 'maumercado@gmail.com',
      url   = 'http://github.com/jeasas/pagosonline',
      long_description = read('README'),
      packages = ['pagosonline',],
      install_requires = [],
      classifiers   = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
)
