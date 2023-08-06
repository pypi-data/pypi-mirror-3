"""
Multiple Fibonacci Number Implementations, in Python and C

by Dan Crosta <dcrosta@late.am>

This package implements four functions to generate the Nth fibonacci number:

* a recursive algorithm in Python
* an iterative algorithm in Python
* and the same two algorithms in C as an extension module

You shouldn't use this package. It's purpose is to serve as an example to
support my "Python Packaging for Humans" presentation at PyGotham II on
June 8, 2012 in New York City.
"""

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from distutils.core import Extension

setup(
    name='multifib',
    version='0.1',
    description='Multiple Fibonacci Number Implementations, in Python and C',
    long_description=__doc__,
    author='Dan Crosta',
    author_email='dcrosta@late.am',
    license='BSD',

    packages=find_packages(),
    ext_modules=[Extension('_cmultifib', ['_cmultifib.c'])],

    setup_requires=['nose'],
    tests_require=['coverage'],
)
