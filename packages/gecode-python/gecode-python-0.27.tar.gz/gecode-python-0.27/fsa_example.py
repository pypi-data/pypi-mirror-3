from gecode import *
from gecode.fsa import FSA,RE

re1 = RE(0).PLUS >> RE(0,1).PLUS
re2 = RE(0,1).PLUS >> RE(1).PLUS

model = space()

XS = model.intvars(5,0,1)
model.extensional(XS,re1)
model.extensional(XS,re2)
model.branch(XS,INT_VAR_SIZE_MIN,INT_VAL_MIN)
for sol in model.search():
    print sol.val(XS)
