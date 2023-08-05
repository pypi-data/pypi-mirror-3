#! /usr/bin/env python

from setuptools import setup
from setuptools import find_packages

setup(
    name='scb',
    version='1.0',
    license='MIT',
    install_requires=[
        'setuptools',
        'xlrd',
        ],
    description='Library for dealing with datasets from SCB.',
    author='Simon Pantzare',
    author_email='simon@pewpewlabs.com',
    url='https://github.com/pilt/scb',
    packages=find_packages(),
    package_data={
        'scb.data': ['*.xls'],
        },
    test_suite='scb.tests',
    )
