#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='purl',
      version='0.1.1',
      url='https://github.com/codeinthehole/purl',
      author="David Winterbottom",
      author_email="david.winterbottom@gmail.com",
      description="A simple URL class for easy URL-building and manipulation",
      long_description=open('README.rst').read(),
      packages=find_packages(),
      )
