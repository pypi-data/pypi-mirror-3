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

from gecode import intset

class Domain(object):

    """Abstraction to code a domain of arbitrary data into integers.
    The codes used form an interval [0,N) where N is the number of data
    elements in the domain."""

    def __init__(self, elems):
        self._encode = {}
        self._decode = {}
        self._elements = tuple(elems)
        self._empty = intset()
        self._full = intset(0,self.size-1)
        for i in range(self.size):
            self._encode[elems[i]] = i
            self._decode[i] = elems[i]

    @property
    def codes(self):
        """iterator over the codes for this domain."""
        return iter(range(self.size))

    @property
    def elements(self):
        """tuple of all elements for this domain (in increasing coding order)."""
        return self._elements

    @property
    def size(self):
        """size for this domain."""
        return len(self._elements)

    @property
    def empty(self):
        """empty intset for this domain."""
        return self._empty

    @property
    def full(self):
        """full intset for this domain."""
        return self._full

    def encode(self, elem):
        """encode a datum into the corresponding integer."""
        return self._encode[elem]

    def decode(self, code):
        """decode an integer into the corresponding datum."""
        return self._decode[code]

    def encode_list(self, elems):
        """encode a list of data into an intset."""
        return intset(map(self.encode,elems))

    def decode_list(self, codes):
        """decode a list of integers into a list of data."""
        return map(self.decode,codes)

    def intvar(self, space):
        """create an intvar ranging over codes for this domain."""
        return space.intvar(self.full)

    def intvars(self, space, n):
        """create a sequence of n intvars, each ranging over codes for this domain."""
        return space.intvar(n, self.full)

    def setvar(self, space, cmin=None, cmax=None):
        """create a setvar ranging over the code sets for this domain."""
        return space.setvar(self.empty, self.full, cmin, cmax)

    def setvars(self, space, n, cmin=None, cmax=None):
        """create a sequence of n setvars, each ranging over the code sets for this domain."""
        return space.setvars(self.empty, self.full, cmin, cmax)
