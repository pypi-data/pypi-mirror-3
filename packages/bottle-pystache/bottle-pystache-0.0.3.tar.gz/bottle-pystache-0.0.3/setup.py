#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from distutils.core import setup

if sys.version_info < (2,5):
    raise NotImplementedError("Sorry, you need at least Python 2.5 or Python 3.x to use bottle.")

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

setup(name='bottle-pystache',
      version='0.0.3',
      description='Bottle Pystache template wrappers',
      long_description='This project is an easy to use Bottle wrapper to Pystache.',
      author='AleiPhoenix',
      author_email='aleiphoenix@gmail.com',
      url='https://github.com/aleiphoenix/bottle-pystache',
      py_modules=['bottle_pystache'],
      scripts=['bottle_pystache.py'],
      license='MIT',
      platforms = 'any',
      cmdclass = {'build_py': build_py}
     )

