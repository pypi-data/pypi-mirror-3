#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''setup for stuf'''

import sys
from os import getcwd
from os.path import join
from setuptools import setup, find_packages


def getversion(fname):
    '''
    Get the __version__ without importing.
    '''
    for line in open(fname):
        if line.startswith('__version__'):
            return '%s.%s.%s' % eval(line[13:].rstrip())


install_requires = list(l for l in open(
    join(getcwd(), 'reqs/requires.txt'), 'r',
).readlines())
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    install_requires.extend(['ordereddict', 'importlib'])

setup(
    name='stuf',
    version=getversion('stuf/__init__.py'),
    description='dictionaries with attribute-style access',
    long_description=open(join(getcwd(), 'README.rst'), 'r').read(),
    keywords='dict attribute collection mapping dot notation access bunch',
    license='BSD',
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    url='https://bitbucket.org/lcrees/stuf',
    packages=find_packages(),
    test_suite='stuf.tests',
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
