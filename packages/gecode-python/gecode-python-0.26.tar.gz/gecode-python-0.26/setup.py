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
from sys import platform as PLATFORM

def gecode_has_gist():
    from distutils.ccompiler import new_compiler
    try:
        from distutils.ccompiler import customize_compiler
    except:
        from distutils.sysconfig import customize_compiler
    import os
    cxx = new_compiler()
    customize_compiler(cxx)
    file_hh = "_gecode_has_gist.hh"
    file_txt = "_gecode_has_gist.txt"
    f = file(file_hh,"w")
    f.write("""#include "gecode/support/config.hpp"
#ifdef GECODE_HAS_GIST
@@T
#else
@@F
#endif
""")
    f.close()
    cxx.preprocess(file_hh,output_file=file_txt)
    f = open(file_txt)
    flag=""
    for line in f:
        if line.startswith("@@"):
            flag = line[2]
            break
    f.close()
    os.remove(file_hh)
    os.remove(file_txt)
    return flag=="T"


if PLATFORM == "darwin":
    XARGS = dict(extra_link_args=["-framework","gecode"])
elif PLATFORM == "win32":
    import os
    XARGS = dict(include_dirs=[os.environ["GECODEDIR"]+"include"],
                 library_dirs=[os.environ["GECODEDIR"]+"lib"])
else:
    LIBS=["stdc++", "gecodeint", "gecodeset", "gecodesearch",
          "gecodekernel", "gecodesupport"]
    if gecode_has_gist():
        LIBS.append("gecodegist")
    XARGS = dict(libraries=LIBS)

setup(
    name='gecode-python',
    description="bindings for the Gecode constraint-programming library",
    author="Denys Duchier",
    author_email="denys.duchier@univ-orleans.fr",
    version="0.26",
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
    py_modules=["gecode.__init__", "gecode.boundvar", "gecode.matrix", "gecode.fsa",
                "gecode.domain"],
    ext_modules=[ 
        Extension("gecode._gecode",
                  sources=["_gecode.cc"],
                  define_macros=[("DISJUNCTOR",None)],
                  language="c++",
                  **XARGS
                  ),
        ]
    )
