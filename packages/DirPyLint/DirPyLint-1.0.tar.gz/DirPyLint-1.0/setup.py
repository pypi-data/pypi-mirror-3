#!/usr/bin/env python

from distutils.core import setup

setup(
    name='DirPyLint',
    version='1.0',
    author='William Farmer',
    author_email='willzfarmer@gmail.com',
    packages=['dirpylint', 'dirpylint.test'],
    url='http://pypi.python.org/pypi/DirPyLint/',
    license='LICENSE.txt',
    description='PyLint for your directories',
    long_description=open('README.txt').read(),
    install_requires=[
        "python-yaml"
    ],
)


