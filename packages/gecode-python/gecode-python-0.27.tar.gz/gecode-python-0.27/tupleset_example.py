from gecode import *

table = ((1,2,3),
         (1,3,2),
         (2,2,3),
         (3,3,3))

model = space()
XS = model.intvars(3,1,3)
model.extensional(XS,table)
model.rel(XS[1],IRT_LQ,XS[2])
model.branch(XS,INT_VAR_SIZE_MIN,INT_VAL_MIN)
for sol in model.search():
    print sol.val(XS)
