# -*- coding: utf-8 -*-
from distutils.core import setup, Extension
import os

pack_dir = os.path.join(os.path.dirname(__file__),"mataraclari")

mathgerecleri = Extension('mataraclari._mathGerecleri',
                    sources = ['mataraclari/mathgerecler.c'])

long_description = """ This package provides couple of functions
for solving some mathematical problems, like finding primes. They are
intended to be very fast, and they are as fast as they can be. Hopefully,
this will spare you from reinventing the whell when you need to do some
basic mathematical calculations. Currently readme file is in Turkish, and
yet no other documentation is available, but this may change in future."""

setup(
    name="mataraclari",
    version = '0.11',
    description = 'Provides some math utilities',
    author = 'Yaşar Arabacı',
    author_email = 'yasar11732@gmail.com',
    long_description = long_description,
    license = "GPL v3",
    url = 'yasar.serveblog.net',
    packages = ["mataraclari"],
    package_dir = {"mataraclari":pack_dir},
    ext_modules = [mathgerecleri],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Mathematics',
        ]
    )
