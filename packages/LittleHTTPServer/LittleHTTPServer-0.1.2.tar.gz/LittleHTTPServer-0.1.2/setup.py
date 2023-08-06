# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from os.path import join as pathjoin

VERSION = "0.1.2"

try:
    LONG_DESCRIPTION = "".join([
        open("README.rst").read(),
        open("CHANGELOG.rst").read(),
    ])
except:
    LONG_DESCRIPTION = ""

REQUIRES = ["distribute"]
if sys.version_info < (2, 7):
    REQUIRES.append("argparse")

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Software Development",
]

setup(
    name="LittleHTTPServer",
    version=VERSION,
    description="Little bit extended SimpleHTTPServer",
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords=["http", "server", "document"],
    author="Tetsuya Morimoto",
    author_email="tetsuya dot morimoto at gmail dot com",
    url="http://bitbucket.org/t2y/littlehttpserver",
    license="Apache License 2.0",
    platforms=['unix', 'linux', 'osx'],
    packages=["littlehttpserver"],
    include_package_data=True,
    install_requires=REQUIRES,
    tests_require=["tox", "pytest", "pep8"],
    entry_points={
        "console_scripts": [
            "littlehttpserver = littlehttpserver.LittleHTTPServer:main",
        ],
    },
)
