#! /usr/bin/env python

from distutils.core import setup

from parse import __version__, __doc__

# perform the setup action
setup(
    name = "parse",
    version = __version__,
    description = "Parse strings using a specification based on the Python format() syntax.",
    long_description = __doc__.decode('utf8'),
    author = "Richard Jones",
    author_email = "rjones@ekit-inc.com",
    py_modules = ['parse'],
    url = 'http://pypi.python.org/pypi/parse',
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
    ],
)

# vim: set filetype=python ts=4 sw=4 et si
