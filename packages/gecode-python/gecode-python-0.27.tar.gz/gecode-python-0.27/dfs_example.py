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

def dfs(s):
    st = s.status()
    if st == SS_SOLVED:
        yield s
    elif st == SS_BRANCH:
        c = s.choice()
        n = c.alternatives()
        stack = [(s,c,0,n)]
        while stack:
            s,c,i,n = stack.pop()
            if i<n-1:
                s2 = s.clone()
                stack.append((s2,c,i+1,n))
            s.commit(c,i)
            st = s.status()
            if st == SS_SOLVED:
                yield s
            elif st == SS_BRANCH:
                c = s.choice()
                n = c.alternatives()
                stack.append((s,c,0,n))
