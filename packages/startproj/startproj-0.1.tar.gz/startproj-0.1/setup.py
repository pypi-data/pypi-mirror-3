#!/usr/bin/env python

from setuptools import setup
import os
import sys

PACKAGE_PATH = 'src'

sys.path.insert(0, PACKAGE_PATH)
import startproj

setup(
    name='startproj',
    url='https://github.com/nathforge/startproj',
    version=startproj.version_string(),
    description='Quickly creates a code directory from a template project',
    
    author='Nathan Reynolds',
    author_email='email@nreynolds.co.uk',
    
    packages=['startproj'],
    package_dir={'': PACKAGE_PATH},
    entry_points={
        'console_scripts': [
            'startproj = startproj.main:main',
        ],
    },
    install_requires=['jinja2'],
)
