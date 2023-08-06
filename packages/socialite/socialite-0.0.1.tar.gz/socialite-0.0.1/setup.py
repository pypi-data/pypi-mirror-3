#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socialite

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='socialite',
    version=socialite.__version__,
    license='Apache 2.0',
    author='Dan Loewenherz',
    author_email='dan@elmcitylabs.com',
    packages=['socialite'],
    package_data={'': ['LICENSE']},
)

