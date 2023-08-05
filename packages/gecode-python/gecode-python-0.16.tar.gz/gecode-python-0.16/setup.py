## -*- python -*-
##=============================================================================
## Copyright (C) 2011 by Denys Duchier
##
## This program is free software: you can redistribute it and/or modify it
## under the terms of the GNU Lesser General Public License as published by the
## Free Software Foundation, either version 3 of the License, or (at your
## option) any later version.
## 
## This program is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with this program.  If not, see <http:##www.gnu.org/licenses/>.
##=============================================================================

from distutils.core import setup
from distutils.extension import Extension

setup(
    name='gecode-python',
    description="bindings for the Gecode constraint-programming library",
    author="Denys Duchier",
    author_email="denys.duchier@univ-orleans.fr",
    version="0.16",
    url="https://launchpad.net/gecode-python",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Programming Language :: Python",
        "Programming Language :: Cython",
        "Programming Language :: C++",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
    package_dir={ "gecode" : "" },
    py_modules=["gecode.__init__", "gecode.boundvar", "gecode.matrix"],
    ext_modules=[ 
        Extension("gecode._gecode",
                  sources=["_gecode.cc"],
                  define_macros=[("DISJUNCTOR",None)],
                  libraries=["stdc++", "gecodeint", "gecodeset", "gecodesearch", "gecodekernel", "gecodesupport"],
                  language="c++"
                  ),
        ]
    )
