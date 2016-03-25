from random import *
import math
import sys

def avg(arr, f):
    s = 0.0
    for el in arr:
        s = s + f(el)
    return s / len(arr)

def hist(arr, f, n):
    narr = map(f, arr)
    _min = min(narr)
    print "min: ", _min
    _max = max(narr)
    print "max: ", _max
    rng = _max - _min
    hst = [0] * n
    for el in narr:
        idx = int(math.floor((el - _min) / rng * n))
        if idx == n:
            idx = n - 1
        hst[idx] = hst[idx] + 1
    return _min, _max, hst 
# World

class World(object):
    def __init__(self, n = 1000, size = 100, neighbour_radius = 4, huntability_addition = 0.1):
        self._n = n
        self._size = size
        self._huntability_addition = huntability_addition
        self._men = []
        self._neighbour_radius = neighbour_radius
        for i in range(self._n):
            self._men.append(self.generate_man())
        self.find_neighbours()
        print "Generated"
    def step(self):
        n = 0
        shuffle(self._men)
        for m in self._men:
            n = n + 1
            m.step()
    def generate_man(self):
        return Man(x = random() * self._size, y = random() * self._size, strength = random(), huntability = random() + self._huntability_addition)
    def find_neighbours(self):
        for m0 in self._men:
            x0, y0 = m0.coords()
            for m in self._men:
                x, y = m.coords()
                d = math.hypot(x-x0, y-y0)
                if (m.id() != m0.id()) and (d <= self._neighbour_radius):
                    m0.add_neighbour(m)
    def print_stats(self):
        #print "Avg neighbours:", avg(self._men, lambda m: len(m.neighbours()))
        print "Avg steal rate:", avg(self._men, lambda m: m.steal_rate()), "%"
        print "Food hist:"
        N = 10
        _min, _max, hst = hist(self._men, lambda m: m.food(), N)
        for i in range(0, N):
            print _min + (_max - _min) * i / N, " ",
        print
        for i in hst:
            print i, " ",
        print

# Methods

class Method(object):
    def __init__(self):
        pass
    def perform(self):
        pass

class Steal(Method):
    def __init__(self, man):
        self.man = man
    def perform(self):
        for m in self.man.neighbours():
            if (m.food() >= 1.0) and (m.strength() < self.man.strength()):
                q = m.take_food()
                self.man.add_food(q)
                self.man.stealed()
                return True
        return False

class Eat(Method):
    def __init__(self, man):
        self.man = man
    def perform(self):
        if self.man.food() >= 1.0:
            self.man.eaten()
            return True
        return False

class Hunt(Method):
    def __init__(self, man):
        self.man = man
    def perform(self):
        #if self.man.id() == 0:
        #    print "Hunt"
        self.man.add_food(self.man.huntability())
        self.man.hunted()
        return True

# Needs

class Need(object):
    def __init__(self):
        self.methods = []
    def satisfy(self):
        pass


class FoodNeed(Need):
    def __init__(self, man):
        self.man = man
        self.methods = [Eat(man), Steal(man), Hunt(man)]
    def satisfy(self):
        for m in self.methods:
            if m.perform():
                break
        self.man.eat()

# Man

class Man(object):
    _next_id = 0
    def __init__(self, x = 0.0, y = 0.0, food = 0.0, strength = 1.0, huntability = 1.0):
        self._x = x
        self._y = y
        self._food = food
        self._strength = strength
        self._needs = [FoodNeed(self)]
        self._neighbours = []
        self._id = Man._next_id
        self._huntability = huntability
        self._stealed = 0.0
        self._hunted = 0.0
        self._eaten = 0.0
        Man._next_id = Man._next_id + 1
    def id(self):
        return self._id
    def coords(self):
        return self._x, self._y
    def food(self):
        return self._food
    def strength(self):
        return self._strength
    def take_food(self):
        f = self._food
        self._food = 0.0
        return f
    def eat(self):
        self._food = self._food - 1.0
        if self._food < 0.0:
            self._food = 0.0
    def add_food(self, q):
        self._food = self._food + q
    def add_neighbour(self, man):
        self._neighbours.append(man)
    def neighbours(self):
        return self._neighbours
    def huntability(self):
        return self._huntability
    def stealed(self):
        self._stealed = self._stealed + 1.0
    def hunted(self):
        self._hunted = self._hunted + 1.0
    def eaten(self):
        self._eaten = self._eaten + 1.0
    def steal_rate(self):
        return self._stealed / (self._hunted + self._stealed + self._eaten) * 100
    def step(self):
        for n in self._needs:
            n.satisfy()


def main():
    seed()
    for r in [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0]:
        print "Huntability addition:", r
        world = World(huntability_addition = r)
        for i in range(1000):
            world.step()
        world.print_stats()

if __name__ == "__main__":
    main()

