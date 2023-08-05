# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


NAME    = "Cmdopt"
VERSION = "0.2.0"
LICENSE = "MIT License"

DESCRIPTION = r'''
Overview
========

Cmdopt.py is command-line option parser for Python.

Example::

    import sys, cmdopt
    ## create parser
    parser = cmdopt.Parser()
    ## define options
    parser.option("-h, --help",       "show help")
    parser.option("-f, --file=FILE",  "read file")
    parser.option("-i, --indent=N",   "indent (default 2)")\
          .validate(lambda val: not val.isdigit() and "integer required.")\
          .handle(lambda val, opts: setattr(opts, 'indent', int(val)))
    ## parse args
    args = sys.argv[1:]
    opts = parser.parse(args)    # may raise cmdopt.ParseError
    if opts.help:
        print(parser.help())     # or parser.help(width=15, indent="  ")

Features:

* Validator
* Handler
* Help message
* Multiple option

See README_ for details.

.. _README: https://bitbucket.org/kwatch/cmdopt/wiki/Cmdopt.py
'''[1:]


def _kwargs():
    name             = NAME
    version          = VERSION
    author           = "Makoto Kuwata"
    author_email     = "kwa@kuwata-lab.com"
    #maintainer       = author
    #maintainer_email = author_email
    url              = "http://pypi.python.org/pypi/%s" % NAME
    description      = "pretty good command-line option parser"
    long_description = DESCRIPTION   # or open("README.txt").read()
    license          = LICENSE
    platforms        = "any"
    download_url     = "http://pypi.python.org/packages/source/%s/%s/%s-%s.tar.gz" % (NAME[0], NAME, NAME, VERSION)

    py_modules       = ["cmdopt"]
    #packages         = ["cmdopt", "cmdopt.sub"]   # or find_packages("lib")
    package_dir      = {"": "lib"}
    #scripts          = ["bin/cmdopt"]
    install_requires = ['PicoTest >=0.2.0']
    #zip_safe         = False

    ## see http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: " + LICENSE,
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ]

    return locals()


setup(**_kwargs())
