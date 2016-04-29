import car
import geom
import cgeom
import track

from bokeh.plotting import figure, curdoc
from bokeh.client import push_session
from bokeh.io import gridplot
from bokeh.charts import HeatMap

import numpy as np
import math
from cacla import CACLA
import random
from autoencoder import MinMax
from pprint import pprint
import os.path

VERY_FAR = 100.0

def none_to_far(x):
    return x if x != None else VERY_FAR

class NetDrawer(object):
    def __init__(self, net):
        self.net = net
        self.figures = []
        self.glyphs = []
        for layer in net.layers:
            fig = figure(x_range=(-2, 40), y_range=(-2, 40),
                    toolbar_location=None, webgl=False,
                    plot_width=300, plot_height=300)
            w = layer.np['w']
            idx = np.indices(w.shape)
            print 'idx:', idx
            sq = fig.square(x=list(idx[0].flat), y=list(idx[1].flat), size=5,
                    color='black', alpha=self.colors(list(w.flat)))
                    #line_color=self.colors(list(w.flat)),
                    #fill_color=self.colors(list(w.flat)))
            #sq = fig.square(x=[10], y=[10], size=5, color='#0000FF',
            #            alpha=[0.5])
            self.figures.append(fig)
            self.glyphs.append(sq)
    
    def colors(self, arr):
        #print 'arr:', arr
        _min = min(arr)
        _max = max(arr)
        d = 1 / (_max - _min)
        cols = [1.0 - (e - _min) * d for e in arr]
        #(0, 0, 0, 1.0 - (e - _min) * d)
        #print 'cols:', cols
        return cols
    
    def draw(self):
        for (l, g) in zip(self.net.layers, self.glyphs):
            w = l.np['w']
            ds = g.data_source
            ds.data['fill_alpha'] = self.colors(list(w.flat))

class Polygon(object):
    def __init__(self, fig=None):
#        O = 31.5
#        I = 28.5
#        outer = geom.Figure([(-O, -O),
#                             (-O, O),
#                             (O, O),
#                             (O, -O)],
#                            close=True, fig=fig)
#        inner = geom.Figure([(-I, -I),
#                             (-I, I),
#                             (I, I),
#                             (I, -I)],
#                            close=True, fig=fig)
#        self.walls = geom.CompoundFigure([outer, inner])

        P = 30.0
        ps = [[-P, -P], [-P, P], [P, P], [P, -P]]

        #self.walls = track.make_track(ps, 3.0, fig=fig)
        self.walls = track.clover(2.0, scale=10.0, fig=fig) #1.5

        self.walls.draw()
        self.car = car.Car((-110.0, 0), (0.0, 1.0), nrays=36, fig=fig, walls=self.walls)
        self._state = self._calc_state()
        self.draw()
        self.ema = 0.0
        self.ema_a = 0.1
    
    def state(self):
        return self._state

    def reset(self):
        angle = random.uniform(-math.pi, math.pi)
        self.car.set_pos((-30.0, -30.0), (math.sin(angle), math.cos(angle)))

    def _calc_state(self):
        rays = self.car.rays()
        #isects = [self.walls.intersect_ext(ray)[1] for ray in rays]
        
        cgeom.rays_figure_intersections(rays, self.walls, self.car.isect_dists, self.car.isects)

        #print 'isects:', isects
        
        #st = np.array([none_to_far(i) for i in isects])
        st = self.car.isect_dists
        st = np.append(st, [self.car.speed, self.car.wheels_angle])
        #print 'state:', st
        return st

    def act(self, action):
        #idx = np.argmax(action)
        #actions = [self.car.act_move,
        #           self.car.act_turn]
        #actions[idx](action[idx]) # TODO: rename
        self.car.act(action)
        self._state = self._calc_state()

    def reward(self):
        hp = 0.0 # hit penalty
        if math.fabs(self.car.speed) < 0.001:
            hp = 1.0
        #self.ema = self.ema_a * self.car.wheels_angle + (1.0 - self.ema_a) * self.ema
        #er = math.fabs(self.ema)
        ap = 2 * math.fabs(self.car.wheels_angle) # angle penalty
        cap = self.car.action_penalty()
        if self.car.speed > 0:
            return self.car.speed - ap - hp - cap
        else:
            return -0.5 * self.car.speed - ap - hp - cap
    
    # Aux
    def draw(self):
        self.car.draw()

def draw_net(net, ds):
    w0 = net.layers[0].np['w']
    idx = np.indices(w0.shape)
    #ds = hm.data_source
    #ds.data['x'] = list(idx[0].flat)
    #ds.data['y'] = list(idx[1].flat)
    #ds.data['values'] = list(w0.flat)
    ds.update({'x': list(idx[0].flat), 'y': list(idx[1].flat), 'values': list(w0.flat)})


class KeyPoints(object):
    def __init__(self, key_points, save_dir, eps = 1.0):
        self.key_points = [np.array(p) for p in key_points]
        self.save_dir = save_dir
        self.eps = eps
        self.current_idx = 0
        self.full_circle = 0
        self.n = 0
        self.sum_reward = 0.0

    def dist(self, tracked_point):
        p = tracked_point - self.key_points[self.current_idx]
        return math.sqrt(p[0]*p[0] + p[1]*p[1])
    
    def update(self, tracked_point, reward):
        self.n += 1
        self.sum_reward += reward
        if(self.dist(tracked_point) < self.eps):
            if self.current_idx == 0:
                self.full_circle = self.n
                self.save()
                self.n = 0
                self.sum_reward = 0.0
            self.current_idx += 1
            if self.current_idx >= len(self.key_points):
                self.current_idx = 0
    
    def save(self):
        with open(os.path.join(self.save_dir, 'full_circle.txt'), 'a') as f:
            f.write(str(self.full_circle) + '\n')
        with open(os.path.join(self.save_dir, 'awg_reward.txt'), 'a') as f:
            f.write(str(self.sum_reward / self.n) + '\n')


    

def main():
    def cmd(a):
        p = (a / (1.0 + math.fabs(a)) + 1.0) / 2.0
        if random.random() > p:
            return -1.0
        else:
            return 1.0

    #def react(a):
    #    return a / (1.0 + math.fabs(a))
    
    random.seed()

    p = figure(x_range=(-120, 120), y_range=(-120, 120), webgl=False, plot_width=750, plot_height=750)
    #, toolbar_location=None
    p.border_fill_color = '#eeeeee'
    p.background_fill_color = 'white'
    p.outline_line_color = None
    p.grid.grid_line_color = None
  
    world = Polygon(p)

    minmax = MinMax([[0.0, 100.0]] * 36 + [[-1.0, 1.0], [-math.pi/4, math.pi/4]])
    learner = CACLA([[-1.0, 1.0]] * 38, dim_actions=2, hidden = 100, sigma=0.1,
            alpha=0.01)
   
    norm_reward = MinMax([[-4.0, 1.0]])

    brain_dir = 'car-brain16'
    try:
        learner.load(brain_dir)
        print "Saved networks have been successfully loaded"
    except Exception as e:
        print e, e.__dict__
        print 'No saved networks'

    #drawer_V = NetDrawer(learner.V.net)
    #drawer_Ac = NetDrawer(learner.Ac.net)

    session = push_session(curdoc())
    #num_layers = len(drawer_V.figures)
    #print 'Num layers:', num_layers
    pq = gridplot([]) #drawer_V.figures, drawer_Ac.figures])
    curdoc().add_root(pq)
    session.show()

    avgrwd = 0.0

    kp = KeyPoints([(-110.0, 0), (110.0, 0)], brain_dir)

    N = 100000 #!!!
    states = np.empty((N, len(world.state()))) #!!!
    for i in xrange(N):
        s = minmax.norm(world.state())
        
        a = learner.getAction(s)
        
        #world.act([cmd(a[0]), cmd(a[1])])
        world.act(a)
        r = world.reward()
        kp.update(world.car.center, r)
        #print world.car.path().points
        if i % 1000 == 0:
            #states[i, :] = s #!!!
            print a, world.car.speed, world.car.wheels_angle, '[', r, ']'
            world.draw()
        #if i % 10000 == 0:
        #    drawer_V.draw()
        #    drawer_Ac.draw()
        if i % 10000 == 0:
            print i, a, world.car.speed, world.car.wheels_angle, 'avgrwd:', avgrwd / 10000.0, '||', kp.full_circle, '||'
            avgrwd = 0.0
        new_s = minmax.norm(world.state())
        avgrwd = avgrwd + r
        nr = norm_reward.norm([r])[0]
        learner.step(s, new_s, a, nr)
        if (i != 0) and (i % 10000 == 0):
            learner.save(brain_dir)
    #np.save('states-2', states)


if __name__ == '__main__':
    main()
