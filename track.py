import geom
import numpy as np

def normalized(v):
    return v / np.linalg.norm(v)

def vec_prod_sign(v1, v2):
    #ax by - ay bx
    v = v1[0] * v2[1] - v1[1] * v2[0]
    if v > 0:
        return 1.0
    else:
        return -1.0

def make_track(points0, d, fig=None, scale=1.0):
    points = [np.array(p) * scale for p in points0]
    ps1 = []
    ps2 = []
    for i, _ in enumerate(points):
        x0 = points[i - 2]
        x1 = points[i - 1]
        x2 = points[i]
        y1 = normalized(x1 - x0)
        y2 = normalized(x1 - x2)
        y = normalized(y1 + y2)
        s = vec_prod_sign(y1, y)
        z1 = x1 + s * d * y
        z2 = x1 - s * d * y
        ps1.append(z1)
        ps2.append(z2)
    f1 = geom.Figure(ps1, close=True, fig=fig)
    f2 = geom.Figure(ps2, close=True, fig=fig)
    return geom.CompoundFigure([f1, f2])

def clover(d, fig=None, scale=1.0):
    return make_track(clover_data, d, fig=fig, scale=scale)

clover_data = [
            [-11, 1.0],
            [-9, 3],
            [-7, 3],
            [-5, 1],
            [-3, 1],
            [-1, 3],
            [-1, 5],
            [-3, 7],
            [-3, 9],
            [-1, 11],
            [1, 11],
            [3, 9],
            [3, 7],
            [1, 5],
            [1, 3],
            [3, 1],
            [5, 1],
            [7, 3],
            [9, 3],
            [11, 1],
            [11, -1],
            [9, -3],
            [7, -3],
            [5, -1],
            [3, -1],
            [1, -3],
            [1, -5],
            [3, -7],
            [3, -9],
            [1, -11],
            [-1, -11],
            [-3, -9],
            [-3, -7],
            [-1, -5],
            [-1, -3],
            [-3, -1],
            [-5, -1],
            [-7, -3],
            [-9, -3],
            [-11, -1]
        ]

