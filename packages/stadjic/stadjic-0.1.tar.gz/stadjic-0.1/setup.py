#!/usr/bin/env python

from distutils.core import setup

setup(
    version='0.1',
    url='https://github.com/nathforge/stadjic',
    name='stadjic',
    description='https://github.com/nathforge/stadjic',
    author='Nathan Reynolds',
    author_email='nath@nreynolds.co.uk',
    packages=['stadjic'],
    package_dir={'': 'src'},
    scripts=['src/stadjic/scripts/stadjic.py'],
)
