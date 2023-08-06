#!/usr/bin/env python

from distutils.core import setup

setup(
    name='DirPyLint',
    version='1.1',
    author='William Farmer',
    author_email='willzfarmer@gmail.com',
    packages=[],
    url='http://pypi.python.org/pypi/DirPyLint/',
    license='LICENSE.txt',
    scripts=['bin/dirpylint.py'],
    description='PyLint for your directories',
    long_description=open('README.txt').read(),
    install_requires=[],
)


