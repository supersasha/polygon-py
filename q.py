import random
import math

class QLearning(object):
    def __init__(self, num_states, num_actions, alpha=0.1, gamma=0.99):
        random.seed()
        self.gamma = gamma
        self.alpha = alpha
        self.nstates = num_states
        self.nactions = num_actions
        self.history = []
        self.action = 0
        self.state = None
        self.q = []
        for i in range(num_states):
            self.q.append([1000000.0] * num_actions)

    def choose_action(self, state):
        if random.random() > 0.1:
            return int(self.max_action(state))
        else:
            return random.randrange(self.nactions)

    def step(self, state, action, reward):
        self.history.append((state, action, reward))

    def learn_history(self):
        for (state, action, reward) in self.history:
            self.learn(state, action, reward)
        self.history = []

    def learn(self, state, action, reward):
        a = self.action
        s = self.state
        q = self.q[s][a]
        learned = reward + self.gamma * self.max_value(state)
        self.q[s][a] = q + self.alpha * (learned - q) # q * (1 - alpha) + alpha * learned
        self.state = state
        self.action = action

    def max_value(self, state):
        A = -1000000000.0
        for a in self.q[state]:
            if a > A:
                A = a
        return A
    
    def max_action(self, state):
        I = -1
        A = -1000000000.0
        for i in range(len(self.q[state])):
            a = self.q[state][i]
            if a > A:
                A = a
                I = i
        return I

    def show(self):
        sz = len(self.q)
        for i in range(sz):
            a = i / 100
            d = i % 100
            print 'Angle:', a, 'Dist:', d, self.q[i]

class World(object):
    def __init__(self, goal_x, goal_y, initPos_x, initPos_y, initCourse, speed = 0.1):
        self.goal = [goal_x, goal_y]
        self.initPos = [initPos_x, initPos_y]
        self.initCourse = initCourse
        self.pos = self.initPos
        self.course = self.initCourse
        self.speed = speed
        self.force_reward = False
    
    def reset(self):
        self.pos = [random.random() * 140.0 - 70.0, random.random() * 140.0 - 70.0] #self.initPos
        self.course = random.random() * 2 * math.pi  #self.initCourse

    def state(self):
        return self.angle() * 100 + int(self.dist())
    
    def dist(self):
        p0 = self.goal
        p = self.pos
        return math.hypot(p0[0] - p[0], p0[1] - p[1])

    def angle(self):
        a = [self.goal[0] - self.pos[0], self.goal[1] - self.pos[1]]
        b = [math.cos(self.course), math.sin(self.course)]
        g = a[0] * b[1] - a[1] * b[0]
        if g < 0:
            return 1
        elif g > 0:
            return 2
        else:
            return 0
    
    def act(self, action):
        iact = int(action)
        if iact == 1: # turnLeft
            self.turnLeft(1)
        elif iact == 2: # turnRight
            self.turnLeft(1)
        elif iact == 3: # turnLeft
            self.turnLeft(5)
        elif iact == 4: # turnRight
            self.turnRight(5)
        elif iact == 5: # turnLeft
            self.turnLeft(20)
        elif iact == 6: # turnRight
            self.turnRight(20)
        elif iact == 7: # turnLeft
            self.turnLeft(60)
        elif iact == 8: # turnRight
            self.turnRight(60)
        old_pos = self.pos
        self.pos = [self.pos[0] + self.speed * math.cos(self.course),
                    self.pos[1] + self.speed * math.sin(self.course)]
        if math.hypot(self.pos[0], self.pos[1]) > 100.0:
            self.pos = old_pos
            self.force_reward = True
        else:
            self.force_reward = False
        #print iact, self.course, self.pos
   
    def turnRight(self, deg):
        self.course = self.course + deg * math.pi / 180.0
        if self.course > 2 * math.pi:
            self.course = self.course - 2 * math.pi

    def turnLeft(self, deg):
        self.course = self.course - deg * math.pi / 180.0
        if self.course < 0:
            self.course = self.course + 2 * math.pi

    def reward(self):
        if self.force_reward:
            return 0
        p0 = self.goal
        p = self.pos

        d = math.hypot(p0[0] - p[0], p0[1] - p[1])
        r = 1.0 / (1.0 + math.fabs(d))
        cosa = (p0[0] - p[0]) * math.cos(self.course) + (p0[1] - p[1]) * math.sin(self.course) / d
        return ((cosa + 1.0) / 2.0 + d) / 2.0

def main():
    world = World(0.0, 0.0, 50.0, 67.0, 0.0, 0.1)
    learner = QLearning(301, 9)
    learner.state = world.state()
    bingo = 0
    for i in range(10000000):
        #print '---------------------'
        #print i
        #print '---------------------'
        for _ in range(100):
            s = world.state()
            a = learner.choose_action(s)
            world.act(a)
            new_s = world.state()
            r = world.reward()
            if world.dist() < 1.0:
                bingo = bingo + 1
                world.reset()
            learner.step(new_s, a, r)
        learner.learn_history()
        if i % 10000 == 0:
            print i, bingo, world.dist()
            bingo = 0
        if i % 100000 == 0:
            learner.show()

if __name__ == '__main__':
    main()

