#!/usr/bin/env python
#coding:utf-8
from __future__ import unicode_literals
from setuptools import setup, find_packages
import codecs
import sys


if sys.version_info[0:2] < (2, 7):
    raise RuntimeError('Requires Python 2.7 or newer')


install_requires = [
    'thriftpy2',
]


tests_require = []


setup(
    name="thriftpywrap",
    version='1.0.0',
    description="Lib to help you build console based thrift servers.",
    long_description=codecs.open('README.rst', mode='r', encoding='utf-8').read(),
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    maintainer="SciELO",
    maintainer_email="tecnologia@scielo.org",
    license="BSD License",
    url="http://docs.scielo.org",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    tests_require=tests_require,
    test_suite='tests',
    install_requires=install_requires,
)
