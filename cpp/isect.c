#include <stdio.h>
#include <math.h>
#include <stdlib.h>

typedef struct intersection
{
    double point[2];
    double dist;
} isx_t;

typedef double vec[2];

/*
 * Incoming arrays are sections of two points
 */ 
isx_t sections_intersect(double * subj, double * obj, int is_ray)
{
    isx_t isx;
    isx.dist = -1.0;
    vec a1;
    if(is_ray) {
        a1[0] = subj[2];
        a1[1] = subj[3];
    } else {
        a1[0] = subj[2] - subj[0];
        a1[1] = subj[3] - subj[1];
    }
    vec a2 = {obj[0] - obj[2], obj[1] - obj[3]};
    vec b = {obj[0] - subj[0], obj[1] - subj[1]};
    double det = a1[0]*a2[1] - a1[1]*a2[0];
    if(fabs(det) > 1e-8) {
        double x0 = (b[0]*a2[1] - b[1]*a2[0]) / det;
        double x1 = (a1[0]*b[1] - a1[1]*b[0]) / det;
        if(x0 >= 0.0 && x1 >= 0.0 && x1 <= 1.0) {
            if(is_ray || (x0 <= 1.0)) {
                isx.dist = x0;
                isx.point[0] = subj[0] + a1[0] * x0;
                isx.point[1] = subj[1] + a1[1] * x0;
                return isx;
            }
        }
    }
    return isx;
}

/*
 * Incoming arrays are sections (double, double) - (double, double).
 * ns - number of sections in subjs
 * no - number of sections in objs
 */
int figures_intersect(double * subjs, int ns, double * objs, int no)
{
    int sz = 4;
    for(double * s = subjs; s < subjs + ns * sz; s += sz) {
        for(double * o = objs; o < objs + no * sz; o += sz) {
            isx_t isx = sections_intersect(s, o, 0);
            if(isx.dist >= 0) {
                return 1;
            }
        }
    }
    return 0;
}

/*
 * Rays are array of (origin, vector) pairs
 * Figure is array of sections
 * Infinity is the far point
 * [OUT] 
 */ 
void rays_figure_intersections(
        double * rays, int nr,
        double * figure, int ns,
        double infinity,
        double * intersections,
        double * distances)
{
    int sz = 4;
    for(double * r = rays, * x = intersections, * d = distances;
            r < rays + nr * sz;
            r += sz, x += 2, d++) {
        isx_t min_isx;
        min_isx.dist = 1.0e20;
        for(double * p = figure; p < figure + ns * sz; p += sz) {
            isx_t isx = sections_intersect(r, p, 1);
            /*
            printf("r = (%f, %f)-(%f, %f), p = (%f, %f)-(%f, %f), isx = [(%f, %f), %f]\n",
                    r[0], r[1], r[2], r[3],
                    p[0], p[1], p[2], p[3],
                    isx.point[0], isx.point[1], isx.dist);
            */
            if(isx.dist >= 0 && isx.dist < min_isx.dist)
                min_isx = isx;
        }
        if(min_isx.dist < 0)
            d[0] = infinity;
        else {
            x[0] = min_isx.point[0];
            x[1] = min_isx.point[1];
            d[0] = min_isx.dist;
        }
    }
}

void recalc_rays(double * rays, int nr, double * center, double * course)
{
    for(int i = 0; i < nr; i++) {
        int n = i * 4;
        double angle = 2 * M_PI * i / nr;
        double s = sin(angle);
        double c = cos(angle);
        rays[n] = center[0];
        rays[n + 1] = center[1];
        rays[n + 2] = c * course[0] - s * course[1];
        rays[n + 3] = s * course[0] + c * course[1];
    }
}

/*

double isect(vec subj0, vec subj1, vec obj0, vec obj1, vec isn)
{
    vec a1 = {subj1[0] - subj0[0], subj1[1] - subj0[1]};
    vec a2 = {obj0[0] - obj1[0], obj0[1] - obj1[1]};
    vec b = {obj0[0] - subj0[0], obj0[1] - subj0[1]};
    double det = a1[0]*a2[1] - a1[1]*a2[0];
    if(fabs(det) > 1e-8) {
        double x0 = (b[0]*a2[1] - b[1]*a2[0]) / det;
        double x1 = (a1[0]*b[1] - a1[1]*b[0]) / det;
        if(x0 >= 0.0 && x0 <= 1.0 && x1 >= 0.0 && x1 <= 1.0)
            if(isn != NULL) {
                isn[0] = subj0[0] + a1[0] * x0;
                isn[1] = subj0[0] + a1[0] * x0; // this is wrong
            }
            return x0;
    }
    return -1.0;
}

void perftest(int f)
{
    vec subj0 = {2, 2};
    vec subj0_prim = {1.9, 2.1};
    vec subj1 = {0.5, 0.5};
    vec obj0 = {0, 1};
    vec obj1 = {1, 1};
    vec isn = {0, 0};
    double r = 0;
    for(int i = 0; i < 1000000001; i++) {
        if((f + i) & 3) {
            r += isect(subj0, subj1, obj0, obj1, isn);
        } else
            r += isect(subj0_prim, subj1, obj0, obj1, isn);
    }
    printf("%f, (%f, %f)\n", r, isn[0], isn[1]);
}

int main(int argc, char ** argv)
{
    int f = 0;
    if(argc > 1)
        f = atoi(argv[1]);
    perftest(f);
    return 0;
}
*/
