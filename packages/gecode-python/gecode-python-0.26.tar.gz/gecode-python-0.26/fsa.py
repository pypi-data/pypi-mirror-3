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

__all__ = ('FSA','RE')

from collections import deque

NONE  = object()

class Counter(object):

    def __init__(self, n=0):
        self.n = n
    def incr(self):
        m = self.n
        self.n += 1
        return m
    def decr(self):
        m = self.n
        self.n -= 1
        return m
    def set_first_not_in(self, s):
        n = self.n
        for i in s:
            if isinstance(i, int) and i>=n:
                n = i+1
        self.n = n

class FSA(object):

    """Finite state automaton."""

    def __init__(self, alphabet=None):
        if alphabet is not None:
            alphabet = frozenset(alphabet)
        self.__alpha = alphabet
        self.__sigma = set()
        self.__edges = set()
        self.__succs = dict()
        self.__preds = dict()
        self.__begs  = set()
        self.__ends  = set()

    @property
    def alphabet(self):
        """returns the alphabet, i.e. the set of legal labels, if it was specified,
        otherwise it returns None."""
        return self.__alpha

    @alphabet.setter
    def alphabet(self, value):
        """sets the alphabet."""
        assert self.__sigma.issubset(value)
        self.__alpha = value

    @property
    def sigma(self):
        """the set of labels used in the FSA (maybe smaller than the alphabet)."""
        return frozenset(self.__sigma)

    def _using_symbol(self, sym):
        if self.__alpha is not None:
            assert sym in self.__alpha
        self.__sigma.add(sym)

    def connect(self, n1, n2, sym):
        """add an edge from n1 to n2 labeled with sym."""
        if sym is not None:
            self._using_symbol(sym)
        edge = (n1,n2,sym)
        self.__edges.add(edge)
        s = self.__succs.get(n1,None)
        if s is None:
            s=set()
            self.__succs[n1] = s
        s.add(edge)
        s = self.__preds.get(n2,None)
        if s is None:
            s=set()
            self.__preds[n2] = s
        s.add(edge)

    @property
    def edges(self):
        """a generator for the (directed) edges."""
        return iter(self.__edges)

    def succs(self, n, sym=NONE):
        """a generator for the successors of n (or sym-successors, if sym is given)."""
        done = set()
        if sym is NONE:
            for n1,n2,lab in self.__succs.get(n,()):
                if n2 not in done:
                    done.add(n2)
                    yield n2
        else:
            for n1,n2,lab in self.__succs.get(n,()):
                if lab==sym and n2 not in done:
                    done.add(n2)
                    yield n2

    def preds(self, n, sym=NONE):
        """a generator for the predecessors of n (or sym-predecessors, if sym is given)."""
        done = set()
        if sym is NONE:
            for n1,n2,lab in self.__preds.get(n,()):
                if n1 not in done:
                    done.add(n1)
                    yield n1
        else:
            for n1,n2,lab in self.__succs.get(n,()):
                if lab==sym and n1 not in done:
                    done.add(n1)
                    yield n1

    def esuccs(self, n):
        """a generator for the out-going edges from n."""
        return iter(self.__succs.get(n,()))

    def epreds(self, n):
        """a generator for the in-coming edges to n."""
        return iter(self.__preds.get(n,()))

    @property
    def zbeg(self):
        """the initial state if it is unique."""
        assert len(self.__begs)==1
        for x in self.__begs:
            return x

    @property
    def zend(self):
        """the final state if it is unique."""
        assert len(self.__ends)==1
        for x in self.__ends:
            return x

    @property
    def begs(self):
        """the set of initial states."""
        return self.__begs

    @property
    def ends(self):
        """the set of final states."""
        return self.__ends

    @property
    def states(self):
        """the set of all states."""
        s = set()
        for n1,n2,sym in self.__edges:
            s.add(n1)
            s.add(n2)
        for n in self.__begs: s.add(n)
        for n in self.__ends: s.add(n)
        return frozenset(s)

    def new(self):
        """return a new instance of this FSA class."""
        return self.__class__()

    def copy(self):
        """return a fresh copy of theis FSA."""
        A = self.new()
        A.__alpha = self.__alpha
        A.__sigma = self.__sigma.copy()
        A.__begs  = self.__begs.copy()
        A.__ends  = self.__ends.copy()
        A.__edges = self.__edges.copy()
        A.__succs = dict((k,v.copy()) for (k,v) in self.__succs.items())
        A.__preds = dict((k,v.copy()) for (k,v) in self.__preds.items())
        return A

    def mirror(self):
        """return the mirror of this FSA.

        The mirror is obtained by reversing the direction of the arrows,
        and exchanging the roles of initial and final states."""
        A = self.new()
        A.__alpha = self.__alpha
        A.__sigma = self.__sigma.copy()
        A.__begs  = self.__ends.copy()
        A.__ends  = self.__begs.copy()
        for n1,n2,sym in self.__edges:
            A.connect(n2,n1,sym)
        return A

    def epsilon_closure(self, nodes):
        """compute the epsilon closure of a collection of nodes.

        The epsilon closure is the set of nodes that can be reached
        from them by traversing 0, 1, or more edges labeled None,
        where None stands for epsilon."""
        stack = list(nodes)
        nodes = set(nodes)
        while stack:
            for other in self.succs(stack.pop(), None):
                if other not in nodes:
                    nodes.add(other)
                    stack.append(other)
        return frozenset(nodes)

    @property
    def is_det(self):
        """True iff the FSA is deterministic."""
        if len(self.__begs) > 1:
            return False
        for edges in self.__succs.values():
            syms = set()
            for n1,n2,sym in edges:
                if sym is None: # epsilon edge
                    return False
                if sym in syms: # two edges with same label
                    return False
                syms.add(sym)
        return True

    def det(self):
        """returns a fresh and deterministic version of this FSA."""
        if self.is_det:
            return self.copy()
        A = self.new()
        seen = set()
        stack = []
        label = self.epsilon_closure(self.begs)
        A.begs.add(label)
        seen.add(label)
        stack.append(label)
        ends = self.ends
        sigma = self.sigma
        while stack:
            label = stack.pop()
            if not label.isdisjoint(ends):
                A.ends.add(label)
            for sym in sigma:
                nexts = set()
                for node in label:
                    nexts.update(self.succs(node, sym))
                if not nexts: continue
                nexts = self.epsilon_closure(nexts)
                if nexts not in seen:
                    seen.add(nexts)
                    stack.append(nexts)
                A.connect(label, nexts, sym)
        return A

    def min(self):
        """returns a fresh, deterministic, minimal version of this FSA."""
        return self.mirror().det().mirror().det()

    def make_error_state(self):
        states = self.states
        n = 0
        while n in states:
            n += 1
        return n

    def complete(self, err=NONE):
        """returns a fresh, complete version of this (deterministic) FSA.

        An FSA is made complete by adding missing transitions for known
        symbols.  This new transitions go to an error state.  If err is
        provided as an argument, it will be used as the error state,
        otherwise a new error state is created.

        if an alphabet was not explicitly specified for the FSA, then it
        will be automatically restricted to the set of symbols actually
        used in it."""
        assert self.is_det
        if err is NONE:
            err = self.make_error_state()
        A = self.copy()
        if A.__alpha is None:
            A.__alpha = frozenset(A.__sigma)
        alpha = self.__alpha
        new_edges = []
        err_used = False
        for node,edges in self.__succs.items():
            syms = frozenset(sym for n1,n2,sym in edges)
            for sym2 in alpha - syms:
                new_edges.append((node,sym2))
                err_used = True
        if err_used:
            for sym in alpha:
                A.connect(err,err,sym)
            for n1,sym in new_edges:
                A.connect(n1,err,sym)
        return A

    def rename(self, how=None, renamings=None):
        """return an equivalent FSA where states have been renamed.

        The renaming strategy is specified by parameter "how":
        None    rename using new object() instances
        N       rename using increasing integers starting from N
        -N      rename using decreasing integers starting from N
        set     rename using first integers not in set
        fsa     rename using the set fsa.states
        str     rename using a format string
        dict    rename using a given mapping

        if parameter "renamings" is not None, then it is a map and we
        update it with the new renamings computed here.
        """

        if how is None:
            def new_name(old):
                return object()
        elif isinstance(how, int) and how >= 0:
            counter = Counter(how)
            def new_name(old):
                return counter.incr()
        elif isinstance(how, int) and how < 0:
            counter = Counter(how)
            def new_name(old):
                return counter.decr()
        elif isinstance(how, (set,frozenset)):
            counter = Counter()
            counter.set_first_not_in(how)
            def new_name(old):
                return counter.incr()
        elif isinstance(how, FSA):
            counter = Counter()
            counter.set_first_not_in(how.states)
            def new_name(old):
                return counter.incr()
        elif isinstance(how, dict):
            def new_name(old):
                return how.get(old, old)
        elif isinstance(how, (str, unicode)):
            def new_name(old):
                return how % old
        else:
            raise TypeError("unknown renaming method: %s" % how)
        # we rename breadth-first starting from the initial states
        table = {}
        queue = deque(self.__begs)
        while queue:
            n = queue.popleft()
            if n not in table:
                n2 = new_name(n)
                table[n] = n2
                queue.extend(self.succs(n))
        for n in self.__ends:
            if n not in table:
                n2 = new_name(n)
                table[n] = n2
        for n in self.states:
            if n not in table:
                n2 = new_name(n)
                table[n] = n2
        A = self.new()
        A.__alpha = self.__alpha
        A.__sigma = self.__sigma.copy()
        def lookup(n):
            return table[n]
        A.__begs = set(map(lookup, self.__begs))
        A.__ends = set(map(lookup, self.__ends))
        for n1,n2,sym in self.edges:
            A.connect(table[n1],table[n2],sym)
        if renamings is not None:
            renamings.update(table)
        return A

    def neg(self):
        """return the negation of this (deterministic) FSA.
        
        The negation of a complete deterministic FSA is obtained
        by making accepting states non accepting, and vice-versa.
        Here the FSA will be automatically completed, but it will
        not be automatically determinized (an exception will be raised)."""
        A = self.complete()
        A.ends = A.states - A.ends
        return A

    def __neg__(self):
        return self.neg()

    def union(self, other):
        """return the union of two FSA.

        they must have disjoint set of states."""
        assert self.states.isdisjoint(other.states)
        A = self.copy()
        A.__alpha = self._combined_alphabet(other)
        A.__sigma |= other.__sigma
        A.__begs  |= other.__begs
        A.__ends  |= other.__ends
        A.__edges |= other.__edges
        A.__succs.update(other.__succs)
        A.__preds.update(other.__preds)
        return A

    def _combined_alphabet(self, other):
        if self.__alpha is None:
            if other.__alpha is None:
                return None
            else:
                assert self.__sigma.issubset(other.__alpha)
                return other.__alpha
        elif other.__alpha is None:
            assert other.__sigma.issubset(self.__alpha)
            return self.__alpha
        else:
            assert self.__alpha == other.__alpha
            return self.__alpha

    def UNION(self, other):
        """return the union of two FSA, making them disjoint if necessary."""
        if not self.states.isdisjoint(other.states):
            other = other.rename(self)
        return self.union(other)

    def __or__(self, other):
        return self.UNION(other)

    def concat(self, other):
        """return a fresh FSA that is the concatenation of two disjoint FSA.

        The concatenation is obtained by linking every final state
        of the first one to every initial state of the second one
        using epsilon transitions."""
        assert self.states.isdisjoint(other.states)
        A = self.copy()
        A.__alpha = self._combined_alphabet(other)
        A.__sigma |= other.__sigma
        A.__edges |= other.__edges
        A.__succs.update((k,v.copy()) for (k,v) in other.__succs.items())
        A.__preds.update((k,v.copy()) for (k,v) in other.__preds.items())
        for n1 in self.ends:
            for n2 in other.begs:
                A.connect(n1,n2,None)
        A.__ends = other.ends.copy()
        return A

    def CONCAT(self, other):
        """returns the concatenation of two FSA.  If the second is
        not disjoint, it is renamed."""
        if not self.states.isdisjoint(other.states):
            other = other.rename(self)
        return self.concat(other)

    def __rshift__(self, other):
        return self.CONCAT(other)

    def new_node(self):
        """return a new node (int) not already present in this FSA."""
        states = self.states
        n = 1
        while n in states:
            n += 1
        return n

    def add_begin(self):
        """return a fresh FSA equivalent to this one but with a new unique initial state."""
        A = self.copy()
        b = A.new_node()
        for n in A.__begs:
            A.connect(b,n,None)
        A.__begs = set((b,))
        return A

    def add_end(self):
        """return a fresh FSA equivalent to this one but with a new unique final state."""
        A = self.copy()
        e = A.new_node()
        for n in A.__ends:
            A.connect(n,e,None)
        A.__ends = set((e,))
        return A

    def add_extremities(self):
        """return a fresh FSA equivalent to this one, but with unique initial and final states."""
        return self.add_begin().add_end()

    def opt(self):
        """make this FSA optional."""
        A = self.add_extremities()
        for b in A.begs:
            for e in A.ends:
                A.connect(b,e,None)
        return A

    def star(self):
        """return the Kleene closure of this FSA."""
        A = self.add_extremities()
        for b in A.begs:
            for e in A.ends:
                A.connect(b,e,None)
                A.connect(e,b,None)
        return A

    def plus(self):
        """return the transitive closure of this FSA."""
        A = self.add_extremities()
        for b in A.begs:
            for e in A.ends:
                A.connect(e,b,None)
        return A

    def repeat(self,min=0,max=None):
        assert isinstance(min,int) and min >= 0
        assert max is None or (isinstance(max,int) and max>=min)
        if max is None:
            if min==0:
                return self.star()
            if min==1:
                return self.plus()
            B = self.star()
            for i in range(min):
                B = (self >> B)
            return B
        else:
            B = self.empty()
            for i in range(max-min):
                B = (self.opt() >> B)
            for i in range(min):
                B = (self >> B)
            return B

    def empty(self):
        A = self.new().add_extremities()
        A.connect(A.zbeg,A.zend,None)
        return A

    def delete_edge(self, edge):
        """delete an edge from this FSA."""
        if edge not in self.__edges:
            return
        n1,n2,sym = edge
        self.__succs[n1].remove(edge)
        self.__preds[n2].remove(edge)
        self.__edges.remove(edge)

    def delete_node(self, n):
        """delete a node from this FSA."""
        edges = self.esuccs(n) | self.epreds(n)
        for e in edges:
            self.delete_edge(e)
        if n in self.__succs:
            del self.__succs[n]
        if n in self.__preds:
            del self.__preds[n]
        self.__begs.drop(n)
        self.__ends.drop(n)

    def product(self, other):
        """returns a fresh FSA for the product of the two (deterministic) FSAs.

        A product FSA has states which are pairs of states from the two FSAs,
        and edges which are correspondingly labeled by pairs of symbols.
        Note that the product's alphabet is the cartesian product of the
        alphabets of the two FSAs, even if not all pairs are used."""
        assert self.is_det
        assert other.is_det
        A = self.new()
        if self.__alpha is not None and other.__alpha is not None:
            A.__alpha = frozenset((x,y)
                                  for x in self.__alpha
                                  for y in other.__alpha)
        A.__sigma = set((x,y) for x in self.sigma for y in other.sigma)
        A.__begs  = set((x,y) for x in self.begs  for y in other.begs)
        A.__ends  = set((x,y) for x in self.begs  for y in other.begs)
        stack = []
        stack.extend(A.__begs)
        reached = set(A.__begs)
        while stack:
            x,y = binode = stack.pop()
            for n1,n2,a in self.__succs.get(x,()):
                for m1,m2,b in other.__succs.get(y,()):
                    binode2 = (n2,m2)
                    bisym = (a,b)
                    A.connect(binode,binode2,bisym)
                    if binode2 not in reached:
                        reached.add(binode2)
                        stack.append(binode2)
        A.__ends.intersection_update(reached)
        return A

    def inter(self, other):
        """returns a fresh FSA for the intersection of the two (deterministic) FSAs.

        An intersection FSA is a variant of a product FSA where transitions
        are kept only if both symbols are identical.  Transitions are then
        labeled with symbols rather than pairs of symbols."""
        assert self.is_det
        assert other.is_det
        A = self.new()
        A.__alpha = self._combined_alphabet(other)
        A.__sigma = set((x,y) for x in self.sigma for y in other.sigma)
        A.__begs  = set((x,y) for x in self.begs  for y in other.begs)
        A.__ends  = set((x,y) for x in self.begs  for y in other.begs)
        stack = []
        stack.extend(A.__begs)
        reached = set(A.__begs)
        while stack:
            x,y = binode = stack.pop()
            for n1,n2,a in self.__succs.get(x,()):
                for m1,m2,b in other.succs(y,a):
                    binode2 = (n2,m2)
                    A.connect(binode,binode2,a)
                    if binode2 not in reached:
                        reached.add(binode2)
                        stack.append(binode2)
        A.__ends.intersection_update(reached)
        return A

    def __and__(self, other):
        return self.inter(other)

    def contains(self, other):
        """returns True iff the language of the other FSA is contained in this one's."""
        return bool(self.det().neg().inter(other.det()).min().ends)

    def equiv(self, other):
        """returns True iff the two FSAs recognize the same language."""
        return self.contains(other) and other.contains(self)

    def reachable(self):
        """returns this FSA's set of reachable states."""
        reached = set()
        stack = []
        stack.extend(self.begs)
        while stack:
            n = stack.pop()
            if n in reached: continue
            reached.add(n)
            stack.extend(self.succs(n))
        return reached

    def reach(self):
        """returns a fresh FSA with only the reachable states."""
        A = self.copy()
        unreachable = self.states - self.reachable()
        for n in unreachable:
            A.delete_node(n)
        return A

    def trim(self):
        """returns a fresh FSA with only the reachable states that can reach a final state."""
        return self.reach().mirror().reach().mirror()

    def pp(self):
        """pretty-print the FSA."""
        print "Initial states:",
        for x in self.begs:
            print x,
        print
        print "Final states:",
        for x in self.ends:
            print x,
        print
        print "Edges:"
        for x,y,s in self.edges:
            if s is None:
                s=""
            print "\t%s --(%s)--> %s" % (x, s, y)
        print

    def gecodify(self, minimize=True):
        """return a triple (beg,ends,edges) appropriate for gecode.
        if minimize is True (the default), minimization is performed.
        """
        if minimize:
            auto = self.min().rename(how=0)
        else:
            auto = self.trim().det().rename(how=0)
        return auto.zbeg,tuple(auto.ends),tuple(auto.edges)

#==============================================================================
# Regular Expressions
#
# (RE(1) >> RE(2).STAR >> RE(30,45).OPT).PLUS
#==============================================================================

class Regex(object):
    def SEQ(self, other):
        return RegexSEQ(self, other)
    def __rshift__(self, other):
        return self.SEQ(other)
    def OR(self, other):
        return RegexOR(self, other)
    def __or__(self, other):
        return self.OR(other)
    @property
    def STAR(self):
        return RegexSTAR(self)
    @property
    def PLUS(self):
        return RegexPLUS(self)
    @property
    def OPT(self):
        return RegexOPT(self)
    @staticmethod
    def EPS():
        return RegexEPS()
    def fsa(self, cls=FSA):
        return self._fsa(cls)
    def gecodify(self, minimize=True, cls=FSA):
        return self._fsa(cls).gecodify(minimize=minimize)

class RegexSYM(Regex):
    def __init__(self, sym):
        self.symbol = sym
    def _fsa(self, cls):
        A = cls()
        A.connect(0, 1, self.symbol)
        A.begs.add(0)
        A.ends.add(1)
        return A

class RegexSEQ(Regex):
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2
    def _fsa(self, cls):
        return self.r1._fsa(cls) >> self.r2._fsa(cls)

class RegexOR(Regex):
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2
    def _fsa(self, cls):
        return self.r1._fsa(trans, cls) | self.r2._fsa(trans, cls)

class RegexSTAR(Regex):
    def __init__(self, r):
        self.r = r
    def _fsa(self, cls):
        return self.r._fsa(cls).star()

class RegexPLUS(Regex):
    def __init__(self, r):
        self.r = r
    def _fsa(self, cls):
        A = self.r._fsa(cls)
        return A.plus()

class RegexOPT(Regex):
    def __init__(self, r):
        self.r = r
    def _fsa(self, cls):
        return self.r._fsa(cls).opt()

class RegexREPEAT(Regex):
    def __init__(self, r, min=0, max=None):
        self.r = r
        self.min = min
        self.max = max
    def _fsa(self, cls):
        return self.r._fsa(cls).repeat(min,max)

class RegexEPS(Regex):
    def _fsa(self, cls):
        A = cls()
        A.connect(0, 1, None)
        A.begs.add(0)
        A.ends.add(1)
        return A

class RegexRANGE(Regex):
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi
    def _fsa(self, cls):
        A = cls()
        lo = self.lo
        hi = self.hi
        for i in range(lo,hi+1):
            A.connect(0, 1, i)
        A.begs.add(0)
        A.ends.add(1)
        return A

class REMaker(object):

    def __call__(self, x=NONE, y=NONE):
        if x is NONE:
            return self.EPS()
        if y is NONE:
            return self.SYM(x)
        return self.RANGE(x,y)

    def SYM(self, x):
        return RegexSYM(x)

    def EPS(self):
        return RegexEPS()

    def RANGE(self, lo, hi):
        return RegexRANGE(lo, hi)

RE = REMaker()
