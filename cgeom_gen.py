import cffi

ffi = cffi.FFI()

source = ''

with open('cpp/isect.c', 'r') as f_src:
    source = f_src.read()

ffi.set_source('_cgeom', source, extra_compile_args=['-O2']) #, sources=['cpp/isect.c'])
ffi.cdef('''
int figures_intersect(double * subjs, int ns, double * objs, int no);
void rays_figure_intersections(
        double * rays, int nr,
        double * figure, int ns,
        double infinity,
        double * intersections,
        double * distances);
void recalc_rays(double * rays, int nr, double * center, double * course);
''')

if __name__ == '__main__':
    ffi.compile()
