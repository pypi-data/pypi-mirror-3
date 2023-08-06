#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from htmlgrab.htmlgrab import get_version

setup(
    name='htmlgrab',
    version=get_version(),
    author='Marcelo Iepsen',
    author_email='iepsen@gmail.com',
    description='A simple command line script to generate static web pages.',
    keywords='python, html, grab',
    url='https://github.com/iepsen/python-htmlgrab',
    license='MIT',
    packages=find_packages(),
    scripts=['htmlgrab/htmlgrab.py'],
    download_url='http://pypi.python.org/packages/source/h/htmlgrab/htmlgrab-%s.tar.gz' % get_version(),
)