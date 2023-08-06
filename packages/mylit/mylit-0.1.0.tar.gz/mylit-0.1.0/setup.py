#!/usr/bin/env python

from setuptools import setup

setup(
    name = "mylit",
    version = "0.1.0",
    author = "Stephan Wenger",
    author_email = "wenger@cg.cs.tu-bs.de",
    description = "Literate programming for Python",
    license = "MIT",
    keywords = "literate programming",
    long_description = open("README.txt").read(),
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Filters",
        "Topic :: Text Processing :: Markup :: HTML",
        ],
    download_url = "http://pypi.python.org/pypi/mylit",
    url = "http://packages.python.org/mylit",
    setup_requires=["pygments"],
    py_modules = ["mylit"],
)

