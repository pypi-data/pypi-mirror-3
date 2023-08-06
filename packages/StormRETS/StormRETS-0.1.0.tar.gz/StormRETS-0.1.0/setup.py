#!/usr/bin/env python

from distutils.core import setup

setup(name="StormRETS",
    version="0.1.0",
    author="Paul Trippett",
    author_email="paul@stormrets.com",
    url="http://www.stormrets.com/libraries/python/",
    license='LICENSE.txt',
    description="StormRETS Python Library",
    long_description=open('README.txt').read(),
    packages = ['StormRETS'],
    install_requires = ['Requests>=0.10.6', ]
)