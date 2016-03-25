import math
import numpy
import random
import neurolab as nl
import os.path
import pprint

def normalize(from_lo, from_hi, x, to_lo, to_hi):
    return to_lo + (x - from_lo) * (to_hi - to_lo) / (from_hi - from_lo)

class Approximator(object):
    def __init__(self, ranges, hidden = 12, dim_out = 1, learning_rate = 0.01 ):
        self.dim_in = len(ranges)
        self.dim_out = dim_out
        self.ranges = ranges
        self.hidden = hidden
        self.learning_rate = learning_rate
        self.net = nl.net.newff(ranges, [hidden, dim_out], transf = [nl.trans.TanSig(), nl.trans.PureLin()])
       
        self.net.trainf = nl.train.train_gd
    
    def call(self, x):
        return self.net.sim([x])[0]
    
    def update(self, target, x):
        self.net.train([x], [target],
                epochs = 1, show = None, goal = 0.0, adapt = True,
                lr = self.learning_rate)
    
    def save(self, filename):
        self.net.save(filename)

    def load(self, filename):
        self.net = nl.load(filename)

class CACLA(object):
    def __init__(self, state_ranges, dim_actions = 1, hidden = 12,
            gamma = 0.99, alpha = 0.01, beta = 0.001, sigma = 1.0):
        self.state_ranges = state_ranges
        self.dim_states = len(state_ranges)
        self.dim_actions = dim_actions
        self.gamma = gamma
        self.alpha = alpha
        self.beta = beta
        self.sigma = sigma
        self.var = 1.0
        
        self.log2 = math.log(2) 
        self.kstep = 0

        self.V = Approximator(state_ranges, hidden = hidden)
        self.Ac = Approximator(state_ranges, dim_out = dim_actions, hidden = hidden)

    def sigma_k(self):
        if self.kstep % 301 == 0:
            return self.sigma
        T = 100000.0
        k = self.log2 / T
        s = self.sigma * math.exp(-k * self.kstep)
        if s < 0.01:
            return 0.01
        return s

    def getAction(self, state):
        #s = self.sigma_k()
        s = self.sigma
        if random.random() < 0.01:
            s = self.sigma * 10
        self.kstep = self.kstep + 1

        mu = self.Ac.call(state)
        r = numpy.zeros(self.dim_actions)
        #print 'r:', r
        #print 'mu:', mu
        for i in range(self.dim_actions):
            r[i] = numpy.random.normal(mu[i], s)
        return r

    def step(self, old_state, new_state, action, reward):
        old_state_v = self.V.call(old_state)
        new_state_v = self.V.call(new_state)
        target = reward + self.gamma * new_state_v
        td_error = target - old_state_v
        #print 'VALUE:', old_state_v, new_state_v, td_error
        self.V.update(target, old_state)
        #old_state_new_v = self.V.call(old_state)# !!!
        #delta = old_state_new_v - old_state_v
        #print 'delta:', delta[0], 'target:', target, 'reward:', reward, 'new_state_v:', new_state_v
        if td_error > 0.0:
            #print 'new V:', new_state_v, 'td_error:', td_error
            self.var = (1.0 - self.beta) * self.var + self.beta * td_error * td_error
            n = int(math.ceil(td_error / math.sqrt(self.var)))
            if n > 5:
                print 'n =', n
            for i in range(n):
                self.Ac.update(action, old_state)

    def save(self, path):
        self.V.save(os.path.join(path, 'V.net'))
        self.Ac.save(os.path.join(path, 'Ac.net'))

    def load(self, filename_prefix):
        self.V.load(os.path.join(filename_prefix, 'V.net'))
        self.Ac.load(os.path.join(filename_prefix, 'Ac.net'))
        #numpy.set_printoptions(threshold=10000)
        #print '=' * 30 + ' V ' + '=' * 30 
        #for l in self.V.net.layers:
        #    print l.__dict__
        #print '=' * 30 + ' Ac ' + '=' * 30 
        #for l in self.Ac.net.layers:
        #    print l.__dict__


