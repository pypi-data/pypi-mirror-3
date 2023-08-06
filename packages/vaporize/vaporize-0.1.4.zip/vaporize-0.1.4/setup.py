#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='vaporize',
    description='A clean and consistent library for the Rackspace Cloud / OpenStack',
    long_description=open('./README.rst').read(),
    author='Michael Lavers',
    author_email='kolanos@gmail.com',
    url='https://github.com/kolanos/vaporize',
    version='0.1.4',
    license='MIT',
    install_requires=open('./requirements.txt').readlines(),
    packages=['vaporize'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities',
    ],
)
