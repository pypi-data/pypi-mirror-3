#!/usr/bin/env python

from distutils.core import setup

with open('README.rst') as fd:
    description = fd.read()

setup(
    name='cmdbot',
    version='1.0.0',
    packages=['cmdbot'],
    url='https://github.com/brunobord/cmdbot/',
    author="Bruno Bord",
    author_email='bruno@jehaisleprintemps.net',
    license="MIT",
    platforms='any',
    description="An IRC Bot with a `cmd` attitude",
)
