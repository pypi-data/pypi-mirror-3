#!/usr/bin/env python

import os
import sys

import pushscreen

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

packages = [
    'pushscreen',
]

setup(
    name='pushscreen',
    version=pushscreen.__version__,
    description='Python client for pushscreen.io',
    long_description=open('README.rst').read(),
    author='Philipp Bosch',
    author_email='hello@pb.io',
    url='http://pushscreen.io/',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'pushscreen': 'pushscreen'},
    include_package_data=True,
    install_requires=['requests'],
    license=open('LICENSE').read(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)