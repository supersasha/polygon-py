import numpy as np

import theano.tensor as T
from theano import function
import theano
from theano.ifelse import ifelse

class Section(object):
    @staticmethod
    def intersect():
        subj0 = T.vector('subj0')
        subj1 = T.vector('subj1')
        obj0 = T.vector('obj0')
        obj1 = T.vector('obj1')
        default = T.constant(-1.0, dtype='floatX')
        a1 = subj1 - subj0
        a2 = obj0 - obj1
        b = obj0 - subj0
        det = a1[0]*a2[1] - a1[1]*a2[0]
        adet = T.abs_(det)
        x0 = (b[0]*a2[1] - b[1]*a2[0]) / det
        #x1 = (a1[0]*b[1] - a1[1]*b[0]) / det
        
        #r0 = T.switch((x0 >= 0.0) & (x0 <= 1.0) & (x1 >= 0.0) & (x1 <= 1.0), x0, default)

        r1 = T.switch(adet > 1e-8, x0, default)
        return function([subj0, subj1, obj0, obj1], r1)

def perftest():
    theano.config.profile = True
    f = Section.intersect()
    for i in xrange(100000):
        f([2, 2], [0.5, 0.5], [0, 1], [1, 1])

if __name__ == '__main__':
    perftest()

