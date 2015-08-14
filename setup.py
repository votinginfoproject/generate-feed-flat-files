# -*- coding: utf-8 -*-
import sys, os, re
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Topic :: Software Development",
    "Topic :: Software Development :: XML",
]

setup(
    name='ftff',
    version='1.0',
    description='converts vip feed to flat file appropriate for db importing',
    long_description=open('README.md').read(),
    classifiers=classifiers,
    keywords=[],
    author='Voting Information Project',
    author_email='info@votinginfoproject.org',
    url='https://github.com/votinginfoproject/generate-feed-flat-files',
    license='',
    packages = ['ftff'],
    package_dir = {'ftff':'.'},
    install_requires=[
        'distribute',
        'lxml==3.3.5',
        'python-magic==0.4.6',
        'rarfile==2.6',
        'wsgiref'
    ]
)
