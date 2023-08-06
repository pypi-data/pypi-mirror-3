#!/usr/bin/env python

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

package_directory = os.path.realpath(os.path.dirname(__file__))
readme_path = os.path.join(package_directory, 'README.rst')
requirements_path = os.path.join(package_directory, 'requirements.txt')

setup(
    name='vaporize',
    description='A clean and consistent library for the Rackspace Cloud / OpenStack',
    long_description=open(readme_path, 'r').read(),
    author='Michael Lavers',
    author_email='kolanos@gmail.com',
    url='https://github.com/kolanos/vaporize',
    version='0.1.5',
    license='MIT',
    install_requires=open(requirements_path, 'r').readlines(),
    packages=['vaporize'],
    classifiers=[
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
