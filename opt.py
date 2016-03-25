import numpy as np
import scipy.optimize as op

def f(x):
    return x[0]

def j(x):
    return np.array([1.0, 0.0, 0])

a1 = np.array([0.0, 0.0])
b1 = np.array([2.0, 2.5])

a2 = np.array([2.0, 0.5])
b2 = np.array([3.5, 1.5])

va1 = np.array([-0.5, 1.5])
vb1 = np.array([0.5, 2.0])

va2 = np.array([-0.5, 1.5])
vb2 = np.array([0.0, -1.0])

def f_eqcons(x):
    print 'x:', x
    r = a1 - a2 + (va1 - va2) * x[0] + (b1 - a1) * x[1] + (a2 - b2) * x[2] + (vb1 - va1) * x[1] * x[0] + (va2 - vb2) * x[2] * x[0]
    #return np.array([r[0], r[1], 0.0]).T
    #print r, r[:, 0], r[0, :]
    print 'r:', r
    return r

def f1(x):
    y = f_eqcons(x)
    return y[0]

def f2(x):
    y = f_eqcons(x)
    return y[1]

#res = op.fmin_slsqp(f, np.array([1.0, 1.0, 1.0]), bounds = [(0.0, 1.0)] * 3,
#        f_eqcons = f_eqcons, f_ieqcons = lambda x: np.array([0.0, 0.0]))

res = op.minimize(f, np.ones(3), jac = j, method = 'SLSQP', constraints = [
                                                                    {'type': 'eq', 'fun': f1},
                                                                    {'type': 'eq', 'fun': f2},
                                                                    {'type': 'ineq', 'fun': (lambda x: x[0])},
                                                                    {'type': 'ineq', 'fun': (lambda x: x[1])},
                                                                    {'type': 'ineq', 'fun': (lambda x: x[2])},
                                                                    {'type': 'ineq', 'fun': (lambda x: 1.0 - x[0])},
                                                                    {'type': 'ineq', 'fun': (lambda x: 1.0 - x[1])},
                                                                    {'type': 'ineq', 'fun': (lambda x: 1.0 - x[2])}
                                                                    ])

#res = op.fmin_cobyla(f, np.array([1.0, 1.0, 1.0]), bounds = [(0.0, 1.0)] * 3,
#        cons = )
print res
