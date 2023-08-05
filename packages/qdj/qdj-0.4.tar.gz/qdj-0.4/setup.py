#!/usr/bin/env python

from setuptools import setup
import os
import sys

PACKAGE_PATH = 'src'

sys.path.insert(0, PACKAGE_PATH)
import qdj

setup(
    name='qdj',
    url='https://github.com/nathforge/qdj',
    version=qdj.version_string(),
    description=(
        'QDJ is \'django-admin.py startproject\', but with your own project templates. '
        'The project starter for obsessives with deadlines.'
    ),
    long_description=open('README.rst').read(),
    
    author='Nathan Reynolds',
    author_email='email@nreynolds.co.uk',
    
    packages=['qdj'],
    package_dir={'': PACKAGE_PATH},
    entry_points={
        'console_scripts': [
            'qdj = qdj.cmd:main',
        ],
    },
    install_requires=['jinja2'],
)
