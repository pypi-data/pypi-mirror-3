#!/usr/bin/env python

import pyvote

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'pyvote'
]

setup(
    name='pyvote',
    version=pyvote.__version__,
    description='Python voting with a redis backend',
    long_description="--",
    author='Luis Morales',
    author_email='luis.morales@legendarymonkey.com',
    url='http://pypi.python.org/pypi/pyvote',
    packages = ["pyvote"],
    package_data={'': ['LICENSE']},
    install_requires = ['redis','hiredis'],
    include_package_data=True,
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ),
)

