import numpy as np
from scipy import linalg
import abc
import math

def translate_mtx(x, y):
    return np.matrix([[x,   0.0, 0.0],
                      [0.0,   y, 0.0],
                      [0.0, 0.0, 1.0]])

def rotate_mtx(angle):
    s = math.sin(angle)
    c = math.cos(angle)
    return np.matrix([[  c,   s, 0.0],
                      [ -s,   c, 0.0],
                      [0.0, 0.0, 1.0]])

class Shape(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def move(self, x, y):
        return

    @abc.abstractmethod
    def rotate(angle):
        return

def point(p):
   return np.matrix(np.append(p, 1)).transpose()

class Section(Shape):
    def __init__(self, p0, p1):
        self.section = np.hstack([point(p0), point(p1)])

    def move(self, x, y):
        m = translate_mtx(x, y)
        self.section = m * self.section
    
    def rotate(self, angle):
        m = rotate_mtx(angle)
        self.section = m * self.section

class Path(Shape):
    def __init__(self, ps, close = False):
        ps1 = ps
        if close:
            ps1.append(ps[0])
        self.path = np.hstack([point(p) for p in ps1])

    def move(self, x, y):
        m = translate_mtx(x, y)
        self.path = m * self.path

    def rotate(self, angle):
        m = rotate_mtx(angle)
        self.path = m * self.path

class Ray(Shape):
    def __init__(self, p, angle):
        self.origin = np.matrix(point(p))
        self.direction = np.matrix(point([math.cos(angle), math.sin(angle)]))

    def move(self, x, y):
        m = translate_mtx(x, y)
        self.origin = m * self.origin

    def rotate(self, angle):
        m = rotate_mtx(angle)
        self.direction = m * self.direction


