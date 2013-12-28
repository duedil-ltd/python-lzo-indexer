#!/usr/bin/env python

from setuptools import setup


def read(filename):
    return open(filename).read()

setup(name="lzo-indexer",
    version="0.0.1",
    description="Library for indexing LZO compressed files",
    long_description=read("README.md"),
    author="Tom Arnfeld",
    author_email="tom@duedil.com",
    maintainer="Tom Arnfeld",
    maintainer_email="tom@duedil.com",
    url="https://github.com/duedil-ltd/python-lzo-indexer",
    download_url="https://github.com/duedil-ltd/python-lzo-indexer/archive/release-0.0.1.zip",
    license=read("LICENSE"),
    packages=["lzo_indexer"],
    test_suite="tests.test_indexer",
)
