#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join as pathjoin
from setuptools import setup, find_packages

VERSION = "0.1.0"
LONG_DESCRIPTION = "".join(
    open("README.txt").read(),
)

REQUIRES = [
    "Trac >= 0.12",
]

CLASSIFIERS = [
    "Framework :: Trac",
    "Development Status :: 4 - Beta",
    "Environment :: Web Environment",
    "License :: OSI Approved :: Apache Software License",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development",
]

setup(
    name="TracTicketReferencePlugin",
    version=VERSION,
    description="Provides support for ticket cross reference for Trac",
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords=["trac", "plugin", "ticket", "cross-reference"],
    author="Tetsuya Morimoto",
    author_email="tetsuya dot morimoto at gmail dot com",
    url="http://trac-hacks.org/wiki/TracTicketReferencePlugin",
    license="Apache License 2.0",
    packages=["ticketref"],
    package_data={
        "ticketref": ["templates/*.html", "htdocs/*.js", "htdocs/*.css",
                      "templates/*.png"],
    },
    include_package_data=True,
    install_requires=REQUIRES,
    entry_points = {
        "trac.plugins": [
            "ticketref.web_ui = ticketref.web_ui",
            "ticketref.api = ticketref.api",
        ]
    }
)
