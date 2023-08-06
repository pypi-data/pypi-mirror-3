#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='SPIlib',
    version='0.1.0',
    description='A small library to use the SPIdev linux interface',
    long_description=open('README.txt').read(),
    author='Stefano Cavallari',
    author_email='spiky.kiwi@gmail.com',
    url="http://pypi.python.org/pypi/SPIlib/",
    install_requires=[
        #"Foobar>=0.1",
    ],
    license="Public Domain (WTFPL2)",
    packages=['spi',],
    zip_safe=True,
)
