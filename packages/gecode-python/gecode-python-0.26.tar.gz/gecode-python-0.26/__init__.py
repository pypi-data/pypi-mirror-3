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
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##=============================================================================

import gecode._gecode as _gecode
import re

__all__ = ['space','intset']

bindings_version = (0, 26)

space = _gecode.space
intset = _gecode.intset

RE_CONSTANT = re.compile("^[A-Z_]+$")
THIS = globals()

# import all constants and export them again
for x in dir(_gecode):
    if RE_CONSTANT.match(x):
        THIS[x] = getattr(_gecode, x)
        __all__.append(x)

from types import ClassType, TypeType
CLASSTYPES=(TypeType,ClassType)

def inspector(name):
    assert isinstance(name,(str,unicode))
    def mk_inspector(fun):
        if type(fun) in CLASSTYPES:
            fun = fun()
        if not callable(fun):
            raise TypeError("expected a callable: %s" % fun)
        fun.__inspector__ = name
        return fun
    return mk_inspector

__all__.append('inspector')

def textinspector(name):
    assert isinstance(name,(str,unicode))
    def mk_textinspector(fun):
        if type(fun) in CLASSTYPES:
            fun = fun()
        if not callable(fun):
            raise TypeError("expected a callable: %s" % fun)
        fun.__textinspector__ = name
        return fun
    return mk_textinspector

__all__.append('textinspector')

if hasattr(_gecode,'Reify'):
    Reify = _gecode.Reify
    __all__.append('Reify')
