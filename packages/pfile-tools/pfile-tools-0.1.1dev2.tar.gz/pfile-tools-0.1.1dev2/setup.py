#!/usr/bin/env python
import setuptools
from setuptools import setup
import os

import pfile_tools


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='pfile-tools',
    version=pfile_tools.VERSION,
    packages=setuptools.find_packages(),
    license='BSD License',
    long_description=read('README.textile'),
    entry_points = {
        'console_scripts': [
            'dump_pfile_header = pfile_tools.scripts.dump_pfile_header:main',
            'anonymize_pfile = pfile_tools.scripts.anonymize_pfile:main'
        ]
    }
)