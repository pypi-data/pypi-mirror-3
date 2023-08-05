## This file is part of Invenio.
## Copyright (C) 2007, 2008, 2010, 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from distutils.core import setup
from distutils.extension import Extension

source_files = ['intbitset_impl.c', 'intbitset.c']

setup(
    name = 'intbitset',
    version = '1.3',
    description = """
    Defines an intbitset data object to hold unordered sets of
    unsigned integers with ultra fast set operations, implemented via
    bit vectors and Python C extension to optimize speed and memory
    usage.

    Emulates the Python built-in set class interface with some
    additional specific methods such as its own fast dump and load
    marshalling functions.  Uses real bits to optimize memory usage,
    so may have issues with endianness if you transport serialized
    bitsets between various machine architectures.
    """,
    author = 'Invenio developers (Samuele Kaplun)',
    author_email = 'info@invenio-software.org',
    url = 'http://invenio-software.org/',
    ext_modules=[
        Extension("intbitset", sources=source_files, extra_compile_args=['-O3']),
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Cython",
        "Programming Language :: C",
        "Topic :: Software Development :: Libraries",
    ],
    provides=["intbitset"],
)
