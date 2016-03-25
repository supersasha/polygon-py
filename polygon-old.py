class Polygon(object):
    def move(self):
        for car in self.cars:
            car.move()
        n = len(self.cars)
        for i in xrange(i):
            c1 = self.cars[i]
            for j in xrange(n):
                if i != j:
                    c2 = self.cars[j]
                    if not c1.is_bumped() or not c2.is_bumped():
                        if c1.intersects(c2):
                            c1.set_bumped()
                            c2.set_bumped()
            if not c1.is_bumped() and c1.intersects(self.obstacles):
                c1.set_bumped()
            c1.finish_action()
    
    def compute_state(self):
        n = len(self.cars)
        for car in self.cars:
            other_cars = [for c in self.cars if c.ID != car.ID]
            car.update_rays_state(other_cars + self.obstacles)

class Ray(object):
    def update(self, shapes):
        for shape in shapes:
            dist = self.intersection_dist(shape)
            if dist < self.value:
                self.value = dist

    def reset(self):
        self.value = 1.0e6

class Car(object):
    def __init__(self):
        self.bumped = False
        self.rays = ...

    def state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def act(self, action):
        self.bumped = False
        # move car according to movement model

    def reward(self):
        return None

    def set_bumped(self):
        self.bumped = True

    def update_rays_state(self, shapes):
        for ray in self.rays:
            ray.reset()
            ray.update(shapes)

    def is_bumped(self):
        return self.bumped

    def finish_action(self):
        # if bumped return to previous position
