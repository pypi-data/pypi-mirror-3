#!/usr/bin/env python

import re
from distutils.core import setup

setup(
  name='metrica',
  version='1.1.1',
  description='Data logging system',
  author='Max Hodak',
  author_email='maxhodak@gmail..com',
  url='http://metri.ca/about',
  requires = [
    "simplejson (>= 2.3)", "requests (>= 0.10)"
  ],
  scripts = ['bin/metrica']
)