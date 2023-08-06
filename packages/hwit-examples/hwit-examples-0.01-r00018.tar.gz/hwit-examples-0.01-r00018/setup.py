#!/usr/bin/env python
#   vim: fileencoding=utf-8

#   copyright 2012 D Haynes

import os.path

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
    from setuptools import find_packages

try:
    _long_descr = open(os.path.join(
        os.path.dirname(__file__), "README.txt"),
        'r').read()
except IOError:
    _long_descr = ""

try:
    from hwit.examples.about import version
except ImportError:
    try:
        from hwit.examples.doc.conf import release as version
    except ImportError:
        version = "0.00"

# Distribute is under heavy development. It's important
# to pin to known-good versions. See
# https://bitbucket.org/tarek/distribute/issues/
_distribute_spec = "distribute" + ','.join([
    ">=0.6.14", # 0.6.14 known good
    "!=0.6.17", # bug with namespace packages
    "!=0.6.26", # setup.py install --user fail
])

setup(
    name="hwit-examples",
    version=version,
    description="Examples for use with HWIT",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    license="COPYING",
    url="http://hwit.org",
    long_description=_long_descr,
    classifiers=[
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
    ],
    namespace_packages = ["hwit"],
    packages=find_packages(),
    package_data = {
        "": ["COPYING", "README.txt", "INSTALL.txt"],
        "hwit.examples.doc": ["*.rst", "_build/html/*.js", "_build/html/*.html", "_build/html/_static/*"],
        "hwit.examples.common": ["*.hwit", "*.tsv", "*.cfg"]
    },
    exclude_package_data = {
        "hwit.examples.common": ["*.txt", "*.css"]
    },
    setup_requires=[
    ],
    install_requires=[
    ],
    entry_points={
        "console_scripts": [
        ],
        "thuswise.hugo.composer": [
            "source = hwit.examples.composition:source",
            "binary = hwit.examples.composition:binary"
        ],
        "thuswise.hugo.fixture": [
        ],
        "thuswise.hugo.testloader": [
        ],
    },
    extras_require={
    }
)
