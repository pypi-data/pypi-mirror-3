# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


NAME    = "Kwartzite"
VERSION = "0.0.1"
LICENSE = "MIT License"

DESCRIPTION = open('README.rst').read()


def _kwargs():
    name             = NAME
    version          = VERSION
    author           = "makoto kuwata"
    author_email     = "kwa@kuwata-lab.com"
    #maintainer       = author
    #maintainer_email = author_email
    url              = "http://pypi.python.org/pypi/%s" % NAME
    description      = "Template engine for HTML using plain old html file"
    long_description = DESCRIPTION   # or open("README.txt").read()
    license          = LICENSE
    platforms        = "any"
    download_url     = "http://pypi.python.org/packages/source/%s/%s/%s-%s.tar.gz" % (NAME[0], NAME, NAME, VERSION)

    #py_modules       = ["kwartzite"]
    packages         = ["kwartzite", "kwartzite.parser", "kwartzite.translator"]
    package_dir      = {"": "lib"}
    #package_data     = {"kwartzite": ["data/*.*"]}
    scripts          = ["bin/pykwartzite"]
    #zip_safe         = False

    ## see http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: " + LICENSE,
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        #"Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]

    return locals()


setup(**_kwargs())
