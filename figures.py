import numpy as np
from scipy import linalg

class Section(object):
    """
        a1 + (b1 - a1) * x = a2 + (b2 - a2) * y
        (b1 - a1) * x + (a2 - b2) * y = a2 - a1
    """
    def __init__(self, a, b):
        self.a = np.array(a)
        self.b = np.array(b)

    def intersect(self, sect):
        p, _ = self.intersect_ext(sect)
        return p

    def intersect_ext(self, sect):
        A = np.matrix([self.b - self.a, sect.a - sect.b]).T
        b = np.matrix([sect.a - self.a]).T
        
        try:
            x = linalg.solve(A, b)
            if x[0] >= 0.0 and x[0] <= 1.0 and x[1] >= 0.0 and x[1] <= 1.0:
                return (self.a + (self.b - self.a) * x[0]), x[0]
            else:
                return None, None
        except linalg.LinAlgError:
            return None, None

class Ray(object):
    def __init__(self, origin, vector):
        self.origin = origin
        self.vector = vector

    def intersect(self, sect):
        p, _ = self.intersect_ext(sect)
        return p

    def intersect_ext(self, sect):
        A = np.matrix([self.vector, sect.a - sect.b]).T
        b = np.matrix([sect.a - self.origin]).T
        
        try:
            x = linalg.solve(A, b)
            if x[0] >= 0.0 and x[1] >= 0.0 and x[1] <= 1.0:
                return (self.origin + self.vector * x[0]), x[0]
            else:
                return None, None
        except linalg.LinAlgError:
            return None, None

class Figure(object):
    def __init__(self, points=None, close = False, fig = None):
        self.close = close
        self.set_points(points)
        
        self.fig = fig
        if fig:
            self.line = fig.line(x=[], y=[], line_color="blue")
            self.ds = self.line.data_source

    def set_points(self, points):
        if points:
            self.points = [np.array(p) for p in points]
            if self.close:
                self.points.append(self.points[0])
        else:
            self.points = []
    
    def intersect(self, sect):
        p, _ = self.intersect_ext(sect)
        return p

    def intersect_ext(self, sect):
        sz = len(self.points)
        assert(sz > 1)
        nearest = None
        t_min = float('inf')
        for i in range(sz - 1):
            p, t = sect.intersect_ext(Section(self.points[i], self.points[i+1]))
            if p != None and t < t_min:
                nearest = p
                t_min = t
        return nearest, t_min
    
    def draw(self):
        if self.fig:
            self.ds.data['x'] = [p[0] for p in self.points]
            self.ds.data['y'] = [p[1] for p in self.points]
            self.ds.trigger('data', self.ds.data, self.ds.data)

class CompoundFigure(object):
    def __init__(self, figures):
        self.figures = figures

    def intersect(self, sect):
        p, _ = self.intersect_ext(sect)
        return p

    def intersect_ext(self, sect):
        nearest = None
        t_min = float('inf')
        for f in self.figures:
            p, t = f.intersect_ext(sect)
            if p != None and t < t_min:
                nearest = p
                t_min = t
        return nearest, t_min

    def draw(self):
        for f in self.figures:
            f.draw()

def main():
    s1 = Section([1.0, 1.0], [0.0, 0.0])
    s2 = Section([0.0, 1.0], [1.0, 0.0])

    print s1.intersect(s2)
    
    s1 = Section([0.0, 0.0], [1.0, 0.0])
    s2 = Section([0.0, 0.0], [2.0, 0.0])
    
    print s1.intersect(s2)
    
    s1 = Section([1.0, 1.0], [0.0, 0.0])
    s2 = Section([0.0, 1.0], [0.0, -1.0])
    
    print s1.intersect(s2)
    
    s1 = Section([2.0, 2.0], [0.5, 0.5])
    s2 = Section([0.0, 1.0], [1.0, 1.0])
    
    print s1.intersect(s2)

    f = Figure([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)], close = True)
    print f.intersect(Section((4.0, 2.0), (0.0, -0.5)))

if __name__ == '__main__':
    main()


