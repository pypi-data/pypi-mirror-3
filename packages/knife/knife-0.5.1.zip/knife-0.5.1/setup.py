#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''setup for knife'''

from os import getcwd
from os.path import join
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_requires = list(l.strip() for l in open(
    join(getcwd(), 'requirements.txt'), 'r',
).readlines())

setup(
    name='knife',
    version='0.5.1',
    description='Pythonic remix of underscore.js: Things go in. Things get '
        'knifed. Things go out.',
    long_description=open(join(getcwd(), 'README.rst'), 'r').read(),
    keywords='pipeline filtering chaining iterator functional fluent chaining',
    license='BSD',
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    url='https://bitbucket.org/lcrees/knife',
    packages=['knife'],
    test_suite='knife.tests',
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
