from pybrain.rl.learners.valuebased import ActionValueNetwork, ActionValueTable, NFQ, Q
from pybrain.rl.agents import LearningAgent
from pybrain.rl.experiments import Experiment
from pybrain.rl.environments import Task
from pybrain.rl.environments.environment import Environment

import math
from scipy import array, asarray

class MyEnvironment(Environment):
    def __init__(self, goal_x, goal_y, initPos_x, initPos_y, initCourse, speed = 0.1):
        super(MyEnvironment, self).__init__()
        self.goal = array([goal_x, goal_y])
        self.initPos = array([initPos_x, initPos_y])
        self.initCourse = initCourse
        self.pos = self.initPos
        self.course = self.initCourse
        self.speed = speed

    def reset(self):
        self.pos = self.initPos
        self.course = self.initCourse

    def getSensors(self):
        return array([self.dist(), self.angle()])

    def performAction(self, action):
        iact = int(action)
        if iact == 1: # turnLeft
            self.course = self.course - math.pi / 180.0
            if self.course < 0:
                self.course = self.course + 2 * math.pi
        elif iact == 2: # turnRight
            self.course = self.course + math.pi / 180.0
            if self.course > 2 * math.pi:
                self.course = self.course - 2 * math.pi
        dp = array([self.speed * math.cos(self.course), self.speed * math.sin(self.course)])
        self.pos = self.pos + dp
        print iact, self.course, self.pos
    
    def dist(self):
        p0 = self.goal
        p = self.pos
        return math.hypot(p0[0] - p[0], p0[1] - p[1])

    def angle(self):
        a = self.goal - self.pos
        b = array([math.cos(self.course), math.sin(self.course)])
        g = a[0] * b[1] - a[1] * b[0]
        if g < 0:
            return 1
        elif g > 0:
            return 2
        else:
            return 0

class MyTask(Task):
    def __init__(self, environment):
        super(MyTask, self).__init__(environment)
        #self.setScaling(sensor_limits=[(-100.0, 100.0), (-100.0, 100.0)],
        #                actor_limits=[(0, 359)])

    
    def getReward(self):
        p0 = self.env.goal
        p = self.env.pos

        d = math.hypot(p0[0] - p[0], p0[1] - p[1])
        #cosa = (p0[0] - p[0]) * math.cos(self.env.course) + (p0[1] - p[1]) * math.sin(self.env.course) / d
        #return cosa
        #return -d
        #if d < 0.1:
        #    return 1.0
        #elif d < 1:
        #    return 0.9
        #elif d < 10:
        #    return 0.5
        #elif d < 30:
        #    return 0.1
        #else:
        #    return 0.0
        #r = 1.0 / (1.0 + math.fabs(d))
        print d
        return -d
        

environment = MyEnvironment(0.0, 0.0, 50.0, 87.0, 0.0, 0.1)
controller = ActionValueNetwork(2, 3)
#controller = ActionValueTable(10000, 3)
learner = NFQ()
agent = LearningAgent(controller, learner)
task = MyTask(environment)
experiment = Experiment(task, agent)

for i in range(10000):
    print '-------------------'
    print i
    print '-------------------'
    experiment.doInteractions(100)
    agent.learn()
    agent.reset()
    environment.reset()
