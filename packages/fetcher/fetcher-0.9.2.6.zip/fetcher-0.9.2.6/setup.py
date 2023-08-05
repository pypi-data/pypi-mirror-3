#!/usr/bin/env python
#coding=utf-8

__created__ = "2009/09/27"
__author__ = "xlty.0512@gmail.com"
__author__ = "牧唐 杭州"

from setuptools import setup, find_packages

setup(
    name="fetcher",
    version="0.9.2.6",
    packages=find_packages(),

    install_requires=['chardet'],

    # metadata for upload to PyPI
    author="Mutang(牧唐)",
    author_email="xlty.0512@gmail.com",
    description="simple python fetcher, support head, get, post action, file upload, etc",
    license="New BSD License",
    keywords="python fetcher spider charset",
    url="http://code.taobao.org/trac/fetcher",
    test_suite="tests.fetcher_tests",
    dependency_links=[
        "http://code.taobao.org/svn/fetcher/"
    ],
)
