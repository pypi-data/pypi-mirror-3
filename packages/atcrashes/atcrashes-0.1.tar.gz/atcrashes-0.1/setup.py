#!/usr/bin/env python
#-*- coding: utf-8 -*- #

from distutils.core import setup
import sys

setup(
    name = "atcrashes",
    version = "0.1",
    description = "Like atexit, but for crashes",
    url = "http://github.com/m-r-r/atcrashes",
    author = "Mickaël Raybaud-Roig",
    author_email = "raybaudroigm@gmail.com",
    py_modules = ['atcrashes'],
    classifiers = [
        'Programming Language :: Python',
        'Intended Audience :: Developers'
    ]
)

