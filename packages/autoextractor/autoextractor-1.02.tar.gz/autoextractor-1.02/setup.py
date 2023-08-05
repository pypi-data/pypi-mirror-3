#!/usr/bin/env python

from setuptools import setup, find_packages, Extension

setup(name='autoextractor',
    version='1.02',
    description='Auto copy and extraction tool',
    packages=['autoextractor'],
    entry_points = {
        'console_scripts': [
            'autoextractor = autoextractor.autoextractor:main'
        ]
    },
    install_requires=['argparse']      
)
