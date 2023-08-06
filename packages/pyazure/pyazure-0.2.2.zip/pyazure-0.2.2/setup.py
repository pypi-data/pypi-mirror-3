#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='pyazure',
    version='0.2.2',
    description='Python wrapper around Windows Azure storage and management REST APIs',
    url='https://github.com/bmb/pyazure',
    packages = find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Topic :: Software Development :: Libraries',
    ],
    use_2to3 = True,
)
