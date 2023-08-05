#!/usr/bin/env python

from setuptools import setup
import os
import sys

package_path = 'src'

sys.path.insert(0, package_path)
import qdj

setup(
    version=qdj.version_string(),
    url='https://github.com/nathforge/qdj',
    name='qdj',
    description='QDJ is like "django-admin.py startproject", but with your own project templates.',
    author='Nathan Reynolds',
    author_email='email@nreynolds.co.uk',
    packages=['qdj'],
    package_dir={'': package_path},
    install_requires=['jinja2'],
    entry_points={
        'console_scripts': [
            'qdj = qdj.cmd:main',
        ],
    },
)
