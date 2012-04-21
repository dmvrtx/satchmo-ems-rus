# -*- coding: utf-8 -*-
# vi: set encoding=utf-8:
#
u"""Скрипт установки пакета."""

__version__ = '0.8.2'

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "satchmo_emsrus",
    version = __version__,
    packages = find_packages(),
    include_package_data = True,
    author = 'Valery Sukhomlinov',
    author_email = 'goodguy@good-guy.me',
    license = 'GPL',
    long_description=read('README.rst'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 2.6',
        'Framework :: Django',
        ],
)
