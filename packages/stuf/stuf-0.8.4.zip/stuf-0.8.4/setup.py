# -*- coding: utf-8 -*-
'''setup stuf'''

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_requires = []
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    install_requires.extend(['ordereddict', 'unittest2'])

setup(
    name='stuf',
    version='0.8.4',
    description='''stuf has attributes''',
    long_description=open(os.path.join(os.getcwd(), 'README.rst'), 'r').read(),
    author='L. C. Rees',
    url='https://bitbucket.org/lcrees/stuf/',
    author_email='lcrees@gmail.com',
    license='MIT',
    packages=['stuf'],
    test_suite='stuf.test',
    zip_safe=False,
    keywords='dict attribute collection mapping dot notation access bunch',
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
