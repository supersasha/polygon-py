import math
import numpy as np
from cacla import CACLA
from figures import CompoundFigure, Figure, Section
from mpdata import Producer, Consumer, Director

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Env(object):
    def __init__(self):
        self.pos = np.array([5.0, 4.9])

        self.target = np.array([0.0, 0.0])
        self.targetTrackCenter = np.array([5.0, 5.0])
        self.targetTrackRadius = 3.0
        self.targetAngle = 1.5 * math.pi
        self.targetAngleDelta = -math.pi / 20.0
        self.moveTarget()

        border = Figure([(0.0, 0.0), (0.0, 10.0),
                         (10.0, 10.0), (10.0, 0.0)],
                        close = True)
        obstacle = Figure([(4.0, 5.0), (4.0, 6.0),
                           (9.0, 6.0), (9.0, 5.0)],
                          close = True)

        self.constraints = CompoundFigure([border])#, obstacle])

    def state(self):
        return np.array([self.pos[0], self.pos[1], self.target[0], self.target[1]])
    
    def act(self, action):
        self.movePos(action)

    def reward(self):
        d = self.dist()
        return -d*d

    def moveTarget(self):
        self.targetAngle = self.targetAngle + self.targetAngleDelta
        if self.targetAngle > 2.0 * math.pi:
            self.targetAngle = self.targetAngle - 2.0 * math.pi
        if self.targetAngle < 0.0:
            self.targetAngle = self.targetAngle + 2.0 * math.pi
        self.target[0] = self.targetTrackCenter[0] + \
                            math.cos(self.targetAngle) * self.targetTrackRadius
        self.target[1] = self.targetTrackCenter[1] + \
                            math.sin(self.targetAngle) * self.targetTrackRadius

    def movePos(self, action):
        p, t = self.constraints.intersect_ext(Section(self.pos, action))
        if p != None:
            #print 'p, pos, action:', p, self.pos, action
            if np.linalg.norm(self.pos - p) < 0.01:
                return
            self.pos = self.pos + (action - self.pos) * t * 0.99
            if self.dist() > 10.0 * math.sqrt(2):
                print self.dist(), '!!!'
                exit()
        else:
            #print 'pos, action, self.target:', self.pos, action, self.target
            #old_pos = self.pos
            self.pos = action
            if self.dist() > 10.0 * math.sqrt(2):
                print self.dist(), '???'
                exit()
    
    def dist(self):
        #return math.hypot(self.pos[0] - self.target[0], self.pos[1] - self.target[1])
        return np.linalg.norm(self.pos - self.target)

class GraphProducer(Producer):
    def __init__(self):
        self.world = Env()
        self.min_dist = 100.0
        self.sum_dist = 0.0
        self.learner = CACLA([(-10.0, 10.0)] * 4, hidden = 12,
            dim_actions = 2, sigma = 1.0, gamma = 0.99, alpha = 0.01)

    def produce(self):
        def norm_reward(r):
            return r / 50.0 + 1.0
        def norm_state(s):
            return s / 5.0 - 1.0 
        def denorm_action(a):
            return (a + 1.0) * 5.0
        N = 1000
        min_dist = 100.0
        sum_dist = 0.0
        points = []
        snr = 0
        for i in xrange(N):
            s = self.world.state()
            a = self.learner.getAction(s)
            self.world.act(denorm_action(a))
            new_s = self.world.state()
            r = self.world.reward()
            nr = norm_reward(r)
            snr = snr + nr
            self.learner.step(s, new_s, a, nr)
            self.world.moveTarget()
            
            d = self.world.dist()
            sum_dist = sum_dist + d
            if d < min_dist:
                min_dist = d
            if i > N - 1 - 40:
                points.append(self.world.pos)
                points.append(self.world.target.copy())
        print snr / 1000.0, self.learner.sigma_k(), sum_dist / N, self.world.dist(), min_dist, denorm_action(a), self.world.pos
        return np.array(points)

class GraphDrawer(Consumer):
    def __init__(self):
        self.fig = plt.figure()
        self.line, = plt.plot([], [], 'r*')
        plt.xlim(0.0, 10.0)
        plt.ylim(0.0, 10.0)
        plt.xlabel('x')
        plt.title('test')
        self.fun1 = None
    
    def init(self, fun):
        self.fun1 = fun
        self.line_ani = animation.FuncAnimation(self.fig, self.fun, 2,
                                       interval=50, blit=True)

    def fun(self, _):
        self.fun1()
        return self.line,

    def run(self):
        plt.show()

    def consume(self, data):
        points = np.ndarray((80, 2), buffer = np.array(data))
        self.line.set_data(points.T)
        

def main():
    p = GraphProducer()
    c = GraphDrawer()
    d = Director(p, c)
    c.init(d.step)
    d.start()
    c.run()
    d.stop()

if __name__ == '__main__':
    main()
