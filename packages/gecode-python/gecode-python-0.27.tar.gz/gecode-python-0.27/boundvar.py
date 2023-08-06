__all__ = ('BoundIntVar','BoundBoolVar','BoundSetVar')

class BoundVar(object):
    def __init__(self, s, v):
        self._space = s
        self._var = v
    def assigned(self):
        return self._space.assigned(self._var)

class BoundIntegralVar(BoundVar):
    def min(self):
        return self._space.min(self._var)
    def max(self):
        return self._space.max(self._var)
    def med(self):
        return self._space.med(self._var)
    def val(self):
        return self._space.val(self._var)
    def size(self):
        return self._space.size(self._var)
    def width(self):
        return self._space.width(self._var)
    def regret_min(self):
        return self._space.regret_min(self._var)
    def regret_max(self):
        return self._space.regret_max(self._var)

class BoundIntVar(BoundIntegralVar):
    def ranges(self):
        return self._space.ranges(self._var)
    def values(self):
        return self._space.values(self._var)
    def __str__(self):
        if self.assigned():
            return "%d" % self.val()
        l = []
        for i,j in self.ranges():
            if i==j:
                l.append(str(i))
            else:
                l.append("%d..%d" % (i,j))
        return "[%s]" % (",".join(l))

class BoundBoolVar(BoundIntegralVar):
    def __str__(self):
        if self.assigned():
            return "%d" % self.val()
        return "[0..1]"

class BoundSetVar(BoundVar):
    def glbSize(self):
        return self._space.glbSize(self._var)
    def lubSize(self):
        return self._space.lubSize(self._var)
    def unknownSize(self):
        return self._space.unknownSize(self._var)
    def cardMin(self):
        return self._space.cardMin(self._var)
    def cardMax(self):
        return self._space.cardMax(self._var)
    def lubMin(self):
        return self._space.lubMin(self._var)
    def lubMax(self):
        return self._space.lubMax(self._var)
    def glbMin(self):
        return self._space.glbMin(self._var)
    def glbMax(self):
        return self._space.glbMax(self._var)
    def glbRanges(self):
        return self._space.glbRanges(self._var)
    def lubRanges(self):
        return self._space.lubRanges(self._var)
    def unknownRanges(self):
        return self._space.unknownRanges(self._var)
    def glbValues(self):
        return self._space.glbValues(self._var)
    def lubValues(self):
        return self._space.lubValues(self._var)
    def unknownValues(self):
        return self._space.unknownValues(self._var)
    def __str__(self):
        glb = []
        for i,j in self.glbRanges():
            if i==j:
                glb.append(str(i))
            else:
                glb.append("%d..%d" % (i,j))
        if self.assigned():
            return "{%s}#%d" % (",".join(glb), self.cardMin())
        lub = []
        for i,j in self.lubRanges():
            if i==j:
                lub.append(str(i))
            else:
                lub.append("%d..%d" % (i,j))
        clo = self.cardMin()
        chi = self.cardMax()
        if clo==chi:
            card = str(clo)
        else:
            card = "[%d..%d]" % (clo,chi)
        return "[{%s}..{%s}]#%s" % (",".join(glb), ",".join(lub), card)
