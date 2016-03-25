import numpy as np
from copy import deepcopy
import neurolab as nl
import math
import random

def net_from_layers(minmax0, trained_layers0, untrained_size, last_lin = False):
    minmax = deepcopy(minmax0)
    layers = [deepcopy(l) for l in trained_layers0]
    for l in layers:
        l.initf = None
    print len(minmax), untrained_size
    for i, nn in enumerate(untrained_size):
        layer_ci = len(minmax)
        if i > 0:
            layer_ci = untrained_size[i - 1]
        elif len(layers) > 0:
            layer_ci = layers[-1].co 
        print 'nn:', nn
        transf = nl.trans.TanSig()
        if last_lin and (i == len(untrained_size) - 1):
            transf = nl.trans.PureLin() 
        l = nl.layer.Perceptron(layer_ci, nn, transf)
        l.initf = nl.init.initnw
        layers.append(l)

    net_co = layers[-1].co
    print net_co
    connect = [[i - 1] for i in range(len(layers) + 1)]
    net = nl.core.Net(deepcopy(minmax), net_co, layers, connect,
            nl.train.train_gd, nl.error.SSE())
    return net

def normalize(from_lo, from_hi, x, to_lo, to_hi):
    return to_lo + (x - from_lo) * (to_hi - to_lo) / (from_hi - from_lo)

class MinMax(object):
    def __init__(self, ranges):
        self.ranges = np.array(ranges)

    def norm(self, inp):
        res = np.array([normalize(r[0], r[1], i, -1.0, 1.0)
            for (i, r) in zip(inp, self.ranges)])
        return res

    def norms(self, inps):
        return np.apply_along_axis(self.norm, 1, inps)

    def denorm(self, out):
        res = np.array([normalize(-1.0, 1.0, o, r[0], r[1])
            for (o, r) in zip(out, self.ranges)])
        return res
    
    def denorms(self, outs):
        return np.apply_along_axis(self.denorm, 1, outs)

def autoencode_layers(minmax0, inp0, train_size, untrain_size, epochs=10000):
    minmax = minmax0
    inp = inp0
    layers = []
    for i, s in enumerate(train_size):
        print 'Training layer {} with {} neurons'.format(i, s)
        net = net_from_layers(minmax, [], [s, len(inp[0])])
        net.train(inp, inp, epochs=epochs, goal=1e-20, adapt=True)
        layers.append(net.layers[0])
        inp_net = net_from_layers(minmax, [net.layers[0]], [])
        inp = inp_net.sim(inp)
        minmax = [[-1.0, 1.0]] * s
    return layers
    #return net_from_layers(minmax0, layers, untrain_size)

def test_autoencoders():
    inp = [[x/10.0] for x in range(-10, 10)]
    trg = [[math.sin(x[0])] for x in inp]

    print inp
    print trg

    net = autoencode_deep_net([[-10.0, 10.0]], inp, [10, 9, 8], [1])
    net.train(inp, trg, epochs = 10000, goal=1e-20)
    print trg
    print net.sim(inp)

def test_ff():
    inp = [[float(x)] for x in range(-10, 10)]
    trg = [[math.sin(x[0])] for x in inp]

    print inp
    print trg
    
    net = nl.net.newff([[-10.0, 10.0]], [30, 1])
    net.trainf = nl.train.train_rprop
    net.train(inp, trg, epochs=40000, goal=1e-20)
    
    print net.sim(inp)

def test_real_data():
    data = np.load('states-2.npy')
    minmax = MinMax([[0.0, 100.0]] * 36 + [[-1.0, 1.0], [-math.pi/4, math.pi/4]])
    indices = range(9990)
    random.shuffle(indices)
    indices = indices[0:1000]
    #inp = minmax.norms(data[0:1000, :])
    inp = minmax.norms(data[indices, :])
    print inp
    layers = autoencode_layers([[-1.0, 1.0]] * 38, inp, [35, 30, 25, 22, 18], [2],
            epochs=10000)
    V_net = net_from_layers([[-1.0, 1.0]] * 38, layers, [1], last_lin=True)
    Ac_net = net_from_layers([[-1.0, 1.0]] * 38, layers, [2], last_lin=True)
    V_net.save('V-03.net')
    Ac_net.save('Ac-03.net')

    print 'done'

def fix_transf(filename, sz):
    net = nl.load(filename)
    new_net = net_from_layers([[-1.0, 1.0]] * 38, net.layers[:-1], [sz], last_lin=True)
    new_net.save(filename)

def test_minmax():
    minmax = MinMax([(-1, 3), (2, 4)])
    print minmax.norms([[1, 2], [3, 4]])
    print minmax.denorms([[0.5, -0.5], [1, 0]])

if __name__ == '__main__':
    fix_transf('car-deep-03/Ac.net', 2)
    #test_autoencoders()
    #test_ff()
    #test_real_data()
    #test_minmax()
