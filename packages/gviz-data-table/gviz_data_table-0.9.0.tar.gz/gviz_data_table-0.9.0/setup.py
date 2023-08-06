#!/usr/bin/python
#
# Copyright (C) 2012 Charlie Clark

"""Python utility module Google Visualization Python API."""

__author__ = "Charlie Clark"

from setuptools import setup, find_packages
import sys

requires = []
major, minor = sys.version_info[:2]
if major == 2 and minor < 6:
    requires.append('simplejson')

extra = dict(
    testing=requires + ['nose', 'coverage'],
    docs=requires + ['sphinx', 'repoze.sphinx.autointerface']
    )

setup(
    name="gviz_data_table",
    version="0.9.0",
    description="Python API for Google Visualization",
    long_description="""
    Date Table maps Python objects to the Google Visualization API
""".strip(),
    author=__author__,
    author_email='charlie.clark@clark-consulting.eu',
    license="BSD",
    url="https://bitbucket.org/charlie_x/gviz-data-table",
    packages = find_packages(),
    install_requires=requires,
    tests_require=requires,
    test_suite = 'gviz_data_table',
    extras_require = extra
)
