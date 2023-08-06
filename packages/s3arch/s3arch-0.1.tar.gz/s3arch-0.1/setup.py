#!/usr/bin/env python
from setuptools import setup

setup(
    name='s3arch',
    version='0.1',
    author='Jeremy Carbaugh',
    author_email='jcarbaugh@gmail.com',
    url="https://github.com/jcarbaugh/s3arch/",
    description='Create local backups of S3 buckets',
    py_modules=['s3arch'],
    install_requires=['boto'],
    entry_points={
        'console_scripts': ['s3arch = s3arch:main']},
)
