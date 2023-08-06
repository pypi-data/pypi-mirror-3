#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from baanlib import __version__


setup(
    name='baanlib',
    version=__version__,
    author='Mathias Fussenegger',
    author_email='pip@zignar.net',
    url='http://pypi.python.org/pypi/baanlib/',
    license='LICENSE.txt',
    description='ole automation library around win32com for use with Baan/Infor LN',
    py_modules=['baanlib'],
    install_requires=[
        'mock',
        'pywin32',
    ],
)
