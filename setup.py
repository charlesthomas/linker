#!/usr/bin/env python
from setuptools import setup

NAME = 'linker'
DESCRIPTION = 'link files based on name'
VERSION = open('VERSION').read().strip()
LONG_DESC = open('README.rst').read()
LICENSE = open('LICENSE').read()

setup(
    name=NAME,
    version=VERSION,
    author='Charles Thomas',
    author_email='ch@rlesthom.as',
    packages=['%s' % NAME],
    url='https://github.com/charlesthomas/%s' % NAME,
    license=LICENSE,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    test_suite='tests',
    scripts=['linker/linker.py'],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Topic :: Desktop Environment',
                 'Topic :: System :: Installation/Setup',
                 'Topic :: Utilities']
)
