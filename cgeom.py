import numpy as np
from _cgeom import ffi, lib

def figures_intersect(subj_fig, obj_fig):
    ns = len(subj_fig.sections) / 4
    no = len(obj_fig.sections) / 4
    subjs = ffi.cast('double *', subj_fig.sections.ctypes.data)
    objs =  ffi.cast('double *', obj_fig.sections.ctypes.data)
    res = lib.figures_intersect(subjs, ns, objs, no)
    return res != 0

def rays_figure_intersections(rays, figure, dists, isxs, infinity = -1.0):
    #rays_data_list = []
    #for r in rays:
    #    rays_data_list.extend([r.origin[0], r.origin[1], r.vector[0], r.vector[1]])
    #rays_data_array = np.array(rays_data_list)
    #rays_data = ffi.cast('double *', rays_data_array.ctypes.data)
    #nr = len(rays_data_array) / 4
    rays_data = ffi.cast('double *', rays.ctypes.data)
    nr = len(rays) / 4
    
    fig_data = ffi.cast('double *', figure.sections.ctypes.data)
    ns = len(figure.sections) / 4

    #isxs = np.zeros(nr * 2)
    #dists = np.zeros(nr)
    
    intersections = ffi.cast('double *', isxs.ctypes.data)
    distances = ffi.cast('double *', dists.ctypes.data)

    lib.rays_figure_intersections(rays_data, nr, fig_data, ns, infinity,
            intersections, distances)

    #return (dists, isxs)

