import math
import numpy as np
from cacla import CACLA
from figures import CompoundFigure, Figure, Section

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

        self.constraints = CompoundFigure([border, obstacle])

    def state(self):
        return np.array([self.pos[0], self.pos[1], self.target[0], self.target[1]])
    
    def act(self, action):
        self.movePos(action)
        self.moveTarget()

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
        

def main():
    def norm_reward(r):
        return r / 50.0 + 1.0
    def norm_state(s):
        return s / 10.0
    def denorm_action(a):
        return a * 10.0

    world = Env()
    min_dist = 100.0
    sum_dist = 0.0
    bingo = 0

    learner = CACLA(4, 2, sigma = 0.1, gamma = 0.8, alpha = 0.01)
    for i in range(100000000):
        #print world.target
        s = world.state()
        #print 'old state:', s
        a = learner.getAction(s)
        world.act(denorm_action(a))
        new_s = world.state()
        #print 'new state:', new_s
        r = world.reward()
        learner.step(norm_state(s), norm_state(new_s), a, norm_reward(r))
        
        d = world.dist()
        sum_dist = sum_dist + d
        if d < min_dist:
            min_dist = d
        #if d < 1.0:
        #    bingo = bingo + 1
        #    world.reset()
        if (i % 1000 == 0):
            print i, sum_dist / 1000.0, world.dist(), min_dist, denorm_action(a), world.pos
            bingo = 0
            min_dist = 100.0
            sum_dist = 0.0

if __name__ == '__main__':
    main()
