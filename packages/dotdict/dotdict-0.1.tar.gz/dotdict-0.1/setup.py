#!/usr/bin/env python
# coding: utf-8

from distutils.core import setup
from dotdict import __author__, __version__

setup(
    name='dotdict',
    py_modules=['dotdict'],
    scripts=[],
    version=__version__,
    license='Public Domain',
    platforms=[
        'POSIX', 'Windows', 'MacOS'
    ],
    description='dot style dictionary like JavaScript.',
    author=__author__,
    author_email='kaido@odiak.net',
    url='http://odiak.net',
    keywords=['dotdict', 'dict'],
    classifiers=[
        'License :: Public Domain',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: MacOS :: MacOS 9',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Programming Language :: Python'
    ],
    longdescription='this is dot style dictionary like JavaScript.'
)
