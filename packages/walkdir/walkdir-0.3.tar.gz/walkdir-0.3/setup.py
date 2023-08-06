#!/usr/bin/env python
from distutils.core import setup

setup(
    name='walkdir',
    version=open('VERSION.txt').read().strip(),
    py_modules=['walkdir'],
    license='Simplified BSD License',
    description='Tools to manipulate and filter os.walk() style iteration',
    long_description=open('README.txt').read(),
    author='Nick Coghlan',
    author_email='ncoghlan@gmail.com',
    url='http://walkdir.readthedocs.org',
    requires=['unittest2']
)
