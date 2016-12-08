#!/usr/bin/env python
import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='lbcapi',
    version='1.0',
    packages=['lbcapi'],
    include_package_data=True,
    license='MIT License',
    description='Make API calls to LocalBitcoins API.',
    author='LocalBitcoins Oy',
    author_email='support.team@localbitcoins.com',
    install_requires=[
    ],
    dependency_links=[
    ],
)
