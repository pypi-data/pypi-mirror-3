#!/usr/bin/env python2.6

import sys, os
from setuptools import setup
from distutils.core import Extension
from distutils.sysconfig import get_python_inc

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

dependencies = []
if sys.version_info.major < 3 and sys.version_info.minor < 7:
    dependencies.append('argparse')

setup(
    name = "nimbstor",
    version = "1.0.1-pre1",
    description = "Store incrementally, compressed and encrypted data failsafe in filesystems, sFTP, WebDAV, IMAP or other backends.",
    author = "Oleksandr Kozachuk",
    author_email = "ddeus.pypi@mailnull.com",
    url = "http://pypi.python.org/pypi/nimbstor",
    license = "WTFPL",
    packages = ['nimbstor',],
    ext_modules = [
      Extension("nimbstor.adler64",
	sources = ["nimbstor/adler64.c"],
	include_dirs = [get_python_inc(plat_specific=1)],
      ),
    ],
    long_description = read('README'),
    install_requires = dependencies,
    scripts = ["nimbstor/nimbtar"],
    classifiers = [
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: End Users/Desktop',
      'Intended Audience :: System Administrators',
      'Operating System :: Unix',
      'Operating System :: POSIX',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Topic :: System :: Archiving',
      'Topic :: System :: Archiving :: Backup',
      'Topic :: System :: Archiving :: Compression',
      'Topic :: System :: Archiving :: Mirroring',
      'Topic :: System :: Archiving :: Packaging',
      'Topic :: Utilities',
    ],
    test_suite = 'nimbstor.tests.test_all',
    zip_safe = False,
)
