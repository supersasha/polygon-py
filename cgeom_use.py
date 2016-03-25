import numpy as np
from cgeom import ffi, lib

#lib.perftest(4)
#lib.perftest(5)
#lib.perftest(6)

subj0 = np.array([1.9, 2.1])
subj1 = np.array([0.5, 0.5])
obj0 = np.array([0.0, 1])
obj1 = np.array([1.0, 1])
isn = np.array([0.0, 0.0])

def cst(x):
    return ffi.cast('double *', x.ctypes.data)

s0 = cst(subj0)
s1 = cst(subj1)
o0 = cst(obj0)
o1 = cst(obj1)
rr = cst(isn)

for _ in xrange(1000000):
    d = lib.isect(s0, s1, o0, o1, rr)

print d, isn
