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

from gecode import *

s = space()
x,y = s.intvars(2,0,3)
# disjunctor
d = s.disjunctor()
# 1st clause
c1 = d.clause()
x1,y1 = c1.intvars(2,0,3)
c1.forward([x,y],[x1,y1])
c1.rel(x1,IRT_EQ,0)
c1.rel(y1,IRT_EQ,0)
# 2nd clause
c2 = d.clause()
x2,y2 = c2.intvars(2,0,3)
c2.forward([x,y],[x2,y2])
z2 = c2.intvar(1,2)
c2.linear([-1,1,1],[x2,y2,z2],IRT_EQ,0)
# search
s.branch([x,y],INT_VAR_SIZE_MIN,INT_VAL_MIN)
for sol in s.search():
    print(sol.val([x,y]))
