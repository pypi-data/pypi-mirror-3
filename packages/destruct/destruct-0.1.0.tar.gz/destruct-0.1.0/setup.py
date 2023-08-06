#!/usr/bin/env python

from distutils.core import setup

setup(
    name="destruct",
    version="0.1.0",
    author="Aleksey Zhukov",
    author_email="drdaeman@drdaeman.pp.ru",
    url="https://github.com/drdaeman/destruct",
    packages=[
        "destruct",
        "destruct.types",
        "destruct.fields",
        "destruct.protocols"
    ],
    license="MIT",
    description="Tiny library to parse binary structures into Python objects",
    long_description=open("README.txt", "r").read(),
    platforms="any",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
