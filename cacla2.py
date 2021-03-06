import math
import numpy
import random
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def normalize(from_lo, from_hi, x, to_lo, to_hi):
    return to_lo + (x - from_lo) * (to_hi - to_lo) / (from_hi - from_lo)

class Activator(object):
    def __init__(self):
        pass
    def call(self, x):
        return math.tanh(x)
    def derive(self, x):
        s = math.tanh(x)
        return (1 - s) * (1 + s)

class Approximator(object):
    """
        n - number of inputs
        m - number of inner nodes
    """
    def __init__(self, n = 1, m = 12):
        self.n = n
        self.m = m

        self.f = Activator()

        rnd = numpy.random.random
        self.v = rnd((n, m)) * 2.0 - 1.0
        self.w = rnd(m) * 2.0 - 1.0
        self.b1 = rnd(m) * 2.0 - 1.0
        self.b2 = rnd() * 2.0 - 1.0

    def call(self, x):
        return self._o(x)

    def update(self, value, x):
        v = numpy.zeros((self.n, self.m))
        w = numpy.zeros(self.m)
        b1 = numpy.zeros(self.m)
        b2 = 0.0
        
        for i in range(self.n):
            for j in range(self.m):
                v[i, j] = self.v[i, j] + value * self.derive_v(i, j, x)

        for j in range(self.m):
            w[j] = self.w[j] + value * self.derive_w(j, x)

        for j in range(self.m):
            b1[j] = self.b1[j] + value * self.derive_b1(j, x)
        
        b2 = self.b2 + value
        
        self.v = v
        self.w = w
        self.b1 = b1
        self.b2 = b2

    def derive_w(self, p, x):
        return self.f.call(self._z(p, x))

    def derive_v(self, p, q, x):
        return self.w[q] * x[p] * self.f.derive(self._z(q, x))
        
    def derive_b1(self, q, x):
        return self.f.derive(self._z(q, x)) * self.w[q]
    
    def _o(self, x):
        return self._y(x)

    def _y(self, x):
        s1 = 0.0
        for j in range(self.m):
            s2 = 0.0
            for i in range(self.n):
                s2 = s2 + self.v[i, j] * x[i]
            s1 = s1 + self.w[j] * self.f.call(self.b1[j] + s2)
        return self.b2 + s1
    
    def _z(self, a, x):
        s = 0.0
        for i in range(self.n):
            s = s + self.v[i,a] * x[i]
        return self.b1[a] + s

class ApproximatorVector(object):
    def __init__(self, dim_in, dim_out, m = 12):
        self.dim_in = dim_in
        self.dim_out = dim_out
        self.m = m
        self.av = []
        for i in range(dim_out):
            self.av.append(Approximator(n = dim_in, m = m))

    def call(self, x):
        r = numpy.zeros(self.dim_out)
        for i in range(self.dim_out):
            r[i] = self.av[i].call(x)
        return r

    def update(self, value, x):
        for i in range(self.dim_out):
            self.av[i].update(value, x)

class CACLA(object):
    def __init__(self, dim_states = 1, dim_actions = 1,
            gamma = 0.99, alpha = 0.02, beta = 0.001, sigma = 1.0):
        self.dim_states = dim_states
        self.dim_actions = dim_actions
        self.gamma = gamma
        self.alpha = alpha
        self.beta = beta
        self.sigma = sigma
        self.var = 1.0

        self.V = Approximator(dim_states, m = 24)
        self.Ac = ApproximatorVector(dim_states, dim_actions, m = 24)

    def getAction(self, state):
        mu = self.Ac.call(state)
        r = numpy.zeros(self.dim_actions)
        for i in range(self.dim_actions):
            r[i] = numpy.random.normal(mu[i], self.sigma)
            #print 'mu, r:', mu[i], r[i]
        return r

    def step(self, old_state, new_state, action, reward):
        old_state_v = self.V.call(old_state)
        new_state_v = self.V.call(new_state)
        td_error = reward + self.gamma * new_state_v - old_state_v
        self.V.update(self.alpha * td_error, old_state)
        if td_error > 0.0:
            self.var = (1.0 - self.beta) * self.var + self.beta * td_error * td_error
            n = int(math.ceil(td_error / math.sqrt(self.var)))
            if n > 10:
                print 'n =', n
            for i in range(n):
                fa_action = self.Ac.call(old_state)
                value = self.alpha * (action - fa_action)
                self.Ac.update(value, old_state)

class Env(object):
    def __init__(self, goal_x, goal_y, initPos_x, initPos_y, initCourse, speed = 0.1):
        self.goal = [goal_x, goal_y]
        self.initPos = [initPos_x, initPos_y]
        self.initCourse = initCourse
        self.pos = self.initPos
        self.course = self.initCourse
        self.speed = speed
        self.force_reward = False
    
    def reset(self):
        self.pos = [random.random() * 140.0 - 70.0, random.random() * 140.0 - 70.0]
        self.course = random.random() * 2 * math.pi

    def state(self):
        return numpy.array(self.pos + [self.course])
    
    def dist(self):
        p0 = self.goal
        p = self.pos
        return math.hypot(p0[0] - p[0], p0[1] - p[1])
    
    def act(self, action):
        self.turn(action)
        old_pos = self.pos
        self.pos = [self.pos[0] + self.speed * math.cos(self.course),
                    self.pos[1] + self.speed * math.sin(self.course)]
        if math.hypot(self.pos[0], self.pos[1]) > 100.0:
            self.pos = old_pos
            self.turn(math.pi)
            self.pos = [self.pos[0] + self.speed * math.cos(self.course),
                        self.pos[1] + self.speed * math.sin(self.course)]
   
    def turn(self, angle):
        self.course = self.course + angle
        if self.course > math.pi:
            self.course = self.course - 2 * math.pi
        elif self.course < -math.pi:
            self.course = self.course + 2 * math.pi

    def reward(self):
        d = self.dist()
        return -d*d

def main():
    def norm_state(s):
        return s * numpy.array([0.01, 0.01, 1.0 / math.pi])
    def norm_reward(r):
        return r / 10000.0 
    def denorm_action(a):
        return a * math.pi
    def cut_action(a):
        if a[0] > 1.0:
            return numpy.array([1.0])
        if a[0] < -1.0:
            return numpy.array([-1.0])
        return a
    world = Env(0.0, 0.0, 50.0, 67.0, 0.0, 0.5)
    learner = CACLA(3, 1, sigma=0.01, gamma=0.99)
    print learner.Ac.av[0].call([50, 50, 0])
    print learner.Ac.av[0].call([60, 60, 0])
    bingo = 0
    min_dist = 100.0
    for i in range(100000000):
        s = world.state()
        a = learner.getAction(s)
        old_a = a
        #a = cut_action(a)
        world.act(denorm_action(a[0]))
        new_s = world.state()
        r = world.reward()
        learner.step(norm_state(s), norm_state(new_s), a, norm_reward(r))
        
        d = world.dist()
        if d < min_dist:
            min_dist = d
        if d < 1.0:
            bingo = bingo + 1
            world.reset()
        if (i % 1000 == 0):
            print i, bingo, world.dist(), min_dist, a, old_a
            bingo = 0
            min_dist = 100.0
        if (i != 0) and (i % 1000000 == 0):
            print learner.Ac.av[0].call([50, 50, 0])
            plot_policy(learner.Ac.av[0])

def plot_policy(fa):
    x = numpy.mgrid[-100:100:30j]
    y = numpy.mgrid[-100:100:30j]
    u = numpy.zeros((30, 30))
    v = numpy.zeros((30, 30))
    for i in range(30):
        for j in range(30):
            c = fa.call([x[i], y[j], 0.0])
            u[i, j] = math.cos(c)
            v[i, j] = math.sin(c)
    plt.quiver(x, y, u, v)
    plt.show()


if __name__ == '__main__':
    main()

