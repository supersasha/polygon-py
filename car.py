import numpy as np
import math
from bokeh.plotting import figure, curdoc
from bokeh.client import push_session
import time
import random
import geom
import cgeom

def angle_to_vector(angle):
    return np.array([math.cos(angle), math.sin(angle)])

def nord_to_vector(angle):
    ''' Positive angle - clockwise
    '''
    return np.array([math.sin(angle), math.cos(angle)])

def lperp(v):
    return np.array([-v[1], v[0]])

def rperp(v):
    return -lperp(v)

def turn_around(v, angle):
    s = math.sin(angle)
    c = math.cos(angle)
    m = np.matrix([[c, -s], [s, c]]).T
    return (v * m).A1



class Car(object):
    def __init__(self, center, course, base = None,
            length = 3.0, width = 1.6,
            wheels_angle = 0.0, speed = 0.0,
            fig = None, nrays = 0, walls=None):
        self.set_pos(center, course)
        self.length = length
        self.width = width
        self.base = base or 1.0 * length # 0.75 * length
        self.half_base = self.base / 2.0

        self.nrays = nrays
        self.walls = walls

        self.rays_data = np.zeros(nrays * 4)
        self.isects = np.zeros(nrays * 2)
        self.isect_dists = np.zeros(nrays)

        self.wheels_angle = wheels_angle
        self.speed = speed
        self.accel = 0.3

        self.last_action = np.array([0.0, 0.0])
        
        self.fig = fig
        if fig:
            #self.rect = fig.rect(x=[], y=[], width=[], height=[], angle=[], line_color="#ffffff", color="green")
            #self.ds = self.rect.data_source
            self.ray_glyph0 = fig.segment(x0=[], y0=[], x1=[], y1=[], line_color='red', line_width=2)
            self.ray_glyphs = fig.segment(x0=[], y0=[], x1=[], y1=[], line_color='red')
            self.isect_glyphs = fig.circle(x=[], y=[], color='black', alpha=0.5, size=5)
        self._path = geom.Figure(close=True, fig=fig)

    def set_pos(self, center, course):
        self.course = np.array(course)
        self.center = np.array(center)

    def rays(self):
        #r = []
        #for i in xrange(self.nrays):
        #    angle = 2 * math.pi * i / self.nrays
        #    vector = turn_around(self.course, angle)
        #    ray = geom.Ray(self.center, vector)
        #    r.append(ray)
        #return r
        return self.rays_data

    def recalc_rays(self):
        for i in xrange(self.nrays):
            angle = 2 * math.pi * i / self.nrays
            #vector = turn_around(self.course, angle)
            s = math.sin(angle)
            c = math.cos(angle)
            self.rays_data[4*i] = self.center[0]
            self.rays_data[4*i+1] = self.center[1]
            self.rays_data[4*i+2] = c * self.course[0] - s * self.course[1]#vector[0]
            self.rays_data[4*i+3] = s * self.course[0] + c * self.course[1]#vector[1]

    def save_pos(self):
        self._course = np.array(self.course)
        self._center = np.array(self.center)
    
    def restore_pos(self):
        self.course = np.array(self._course)
        self.center = np.array(self._center)

    def action_penalty(self):
        h = 0.1
        m = 8
        c = 5.0
        a = h / (c ** m)
        la = math.fabs(self.last_action[0])
        p = a * (la ** m)
        return p / (1 + math.fabs(p))

    def act(self, action):
        self.last_action = action
        def d(a):
            return a / (1.0 + math.fabs(a))
        #self.act_turn(action[1])
        #self.act_move(action[0])
        self.speed = d(action[0])
        self.wheels_angle = math.pi / 4.0 * d(action[1])
        self.move_or_stop(0.1)

    def act_move(self, value):
        if value > 0:
            self.act_fwd(value)
        else:
            self.act_back(value)

    def act_fwd(self, value):
        #print 'fwd'
        dt = 0.1
        c = math.cos(self.wheels_angle * 1.5)
        self.speed = self.speed + self.accel * dt
        if self.speed > 10.0 * c:
            self.speed = 10.0 * c
        #self.move_or_stop(0.1)

    def act_back(self, value):
        #print 'back'
        dt = 0.1
        c = math.cos(self.wheels_angle * 1.5)
        self.speed = self.speed - self.accel * dt
        if self.speed < -2.0 * c:
            self.speed = -2.0 * c
        #self.move_or_stop(0.1)

    
    def act_turn(self, value):
        p4 = math.pi / 4.0
        if value > 0.0:
            self.wheels_angle += 0.1
            if self.wheels_angle > p4:
                self.wheels_angle = p4
        else:
            self.wheels_angle -= 0.1
            if self.wheels_angle < -p4:
                self.wheels_angle = -p4

#        #print 'left'
#        th = 0.5
#        if value < -th:
#            self.wheels_angle = self.wheels_angle - 0.01
#            if self.wheels_angle < -math.pi/4:
#                self.wheels_angle = -math.pi/4
#        elif value > th:
#            self.wheels_angle = self.wheels_angle + 0.01
#            if self.wheels_angle > math.pi/4:
#                self.wheels_angle = math.pi/4
#        else:
#            self.wheels_angle = 0.0 #self.wheels_angle * 0.5
#        #self.move_or_stop(0.1)

    def act_left(self, value):
        #print 'left'
        self.wheels_angle = self.wheels_angle - 0.01
        if self.wheels_angle < -math.pi/4:
            self.wheels_angle = -math.pi/4
        #self.move_or_stop(0.1)
    
    def act_right(self, value):
        #print 'right'
        self.wheels_angle = self.wheels_angle + 0.01
        if self.wheels_angle > math.pi/4:
            self.wheels_angle = math.pi/4
        #self.move_or_stop(0.1)

    def move_or_stop(self, dt):
        self.save_pos()
        self.move(dt)
        self.recalc_rays()
        if (self.walls != None) and cgeom.figures_intersect(self.path(), self.walls):
        #self.path().intersect(self.walls) != None:
            self.restore_pos()
            self.speed = 0.0
            #self.wheels_angle = 0.0

    def move(self, dt):
        if math.fabs(self.wheels_angle) < 0.0001:
            self.center = self.center + self.speed * dt * self.course
        else:
            self.move_with_turn(dt)

    def turn_wheels(self, wheels_angle):
        self.wheels_angle = wheels_angle

    def move_with_turn(self, dt):
        beta = -self.speed * dt * math.tan(self.wheels_angle) / self.base
        pg = None
        if self.wheels_angle > 0.0:
            pg = rperp(self.course) #np.array([self.course[1], -self.course[0]])
        else:
            pg = lperp(self.course) #np.array([-self.course[1], self.course[0]])
        rot_center = self.center - self.half_base * self.course + self.base / math.fabs(math.tan(self.wheels_angle)) * pg

        s = math.sin(beta)
        c = math.cos(beta)
        m = np.matrix([[c, -s], [s, c]]).T
        self.center = (rot_center + (self.center - rot_center) * m).A1
        self.course = (self.course * m).A1

    def path(self):
        l = self.length / 2.0 * self.course
        w = rperp(self.course) * self.width / 2
        self._path.set_points([self.center + l - w,
                                 self.center + l + w,
                                 self.center - l + w,
                                 self.center - l - w])
        return self._path
    
    def draw(self):
        if self.fig == None:
            return
        self.path().draw()
        ray_len = 20.0
        rays = self.rays()
        #print 'rays:', rays
        ds = self.ray_glyphs.data_source
        ds.data['x0'] = rays[4::4] #[r.origin[0] for r in rays[1:]]
        ds.data['y0'] = rays[5::4]#[r.origin[1] for r in rays[1:]]
        ds.data['x1'] = rays[4::4] + ray_len * rays[6::4]#[r.origin[0] + ray_len * r.vector[0] for r in rays[1:]]
        ds.data['y1'] = rays[5::4] + ray_len * rays[7::4]#[r.origin[1] + ray_len * r.vector[1] for r in rays[1:]]
        ds = self.ray_glyph0.data_source
        ds.data['x0'] = [rays[0]] #[rays[0].origin[0]]
        ds.data['y0'] = [rays[1]] #[rays[0].origin[1]]
        ds.data['x1'] = [rays[0] + ray_len * 1.1 * rays[2]]#[rays[0].origin[0] + ray_len * 1.1 * rays[0].vector[0]]
        ds.data['y1'] = [rays[1] + ray_len * 1.1 * rays[3]]#[rays[0].origin[1] + ray_len * 1.1 * rays[0].vector[1]]
        #ds.trigger('data', ds.data, ds.data)

        if self.walls:
            ds = self.isect_glyphs.data_source
            #isects = [self.walls.intersect(ray) for ray in rays]
            cgeom.rays_figure_intersections(rays, self.walls, self.isect_dists, self.isects) #[1]
            #print 'isects:', isects
            #ds.data['x'] = [isect[0] for isect in isects if isect != None]
            #ds.data['y'] = [isect[1] for isect in isects if isect != None]
            ds.data['x'] = self.isects[0::2]#[self.isects[2 * i] for i in xrange(len(self.isects)/2)]
            ds.data['y'] = self.isects[1::2]#[self.isects[2 * i + 1] for i in xrange(len(self.isects)/2)]

        #self.ds.data['x'] = [self.center[0]]
        #self.ds.data['y'] = [self.center[1]]
        #self.ds.data['width'] = [self.width]
        #self.ds.data['height'] = [self.length]
        #self.ds.data['angle'] = [math.atan2(self.course[1], self.course[0]) + math.pi/2]
        ##self.ds.trigger('data', self.ds.data, self.ds.data)

def test():
    p = figure(x_range=(-20, 20), y_range=(-20, 20), toolbar_location=None, webgl=False, plot_width=750, plot_height=750)
    p.border_fill_color = '#eeeeee'
    p.background_fill_color = 'white'
    p.outline_line_color = None
    p.grid.grid_line_color = None

    session = push_session(curdoc())
    curdoc().add_root(p)
    session.show()

    car = Car([1.0, 2.0], angle_to_vector(math.pi/2), wheels_angle=0.4, speed=1.0, width=1.0, length=2.0, fig=p, nrays=36)
    border = geom.Figure([[-10.0, -10.0], [-10.0, 10.0], [10.0, 10.0], [10.0, -10.0]],
            close=True, fig=p)
    obstacle = geom.Figure([[-5.0, 0.0], [0.0, 0.0], [0.0, -5.0], [-5.0, -5.0]],
            close=True, fig=p)
    #obstacle = geom.Figure(close=True, fig=p)
    #print border.points
    #obstacle.set_points([[-5.0, 0.0], [0.0, 0.0], [0.0, -5.0], [-5.0, -5.0]])
    env = geom.CompoundFigure([border, obstacle])
    env.draw()
    for i in xrange(10000):
        car.turn_wheels(random.random() - 0.5)
        car.save_pos()
        car.move(0.1)
        if car.path().intersect(env) != None:
            car.restore_pos()
            car.speed = -car.speed
        car.draw(env)
        time.sleep(0.01)

if __name__ == '__main__':
    test()
