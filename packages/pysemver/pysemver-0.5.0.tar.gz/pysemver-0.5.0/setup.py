#!/usr/bin/env python

from distutils.core import setup

import pysemver


setup(name='pysemver',
      version=pysemver.__version__,
      description='Python utilities to work with SemVer-compliant version numbers.',
      long_description=pysemver.__doc__,
      author='Anton Moiseev',
      author_email='a@antonmoiseev.com',
      url='https://github.com/antonmoiseev/pysemver',
      py_modules=['pysemver'],
      license='MIT')