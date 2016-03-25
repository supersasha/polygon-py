#include <stdio.h>
#include <math.h>
#include <stdlib.h>

typedef double vec[2];

double isect(vec subj0, vec subj1, vec obj0, vec obj1)
{
    vec a1 = {subj1[0] - subj0[0], subj1[1] - subj0[1]};
    vec a2 = {obj0[0] - obj1[0], obj0[1] - obj1[1]};
    vec b = {obj0[0] - subj0[0], obj0[1] - subj0[1]};
    double det = a1[0]*a2[1] - a1[1]*a2[0];
    if(fabs(det) > 1e-8) {
        double x0 = (b[0]*a2[1] - b[1]*a2[0]) / det;
        double x1 = (a1[0]*b[1] - a1[1]*b[0]) / det;
        if(x0 >= 0.0 && x0 <= 1.0 && x1 >= 0.0 && x1 <= 1.0)
            return x0;
    }
    return -1.0;
}

void perftest(int f)
{
    vec subj0 = {2, 2};
    vec subj0_prim = {2.1, 2.1};
    vec subj1 = {0.5, 0.5};
    vec obj0 = {0, 1};
    vec obj1 = {1, 1};
    double r = 0;
    for(int i = 0; i < 100000000; i++) {
        if(f < 3) {
            r = isect(subj0, subj1, obj0, obj1);
            f++;
        } else
            r = isect(subj0_prim, subj1, obj0, obj1);
    }
    printf("%f\n", r);
}

int main(int argc, char ** argv)
{
    int f = 0;
    if(argc > 1)
        f = atoi(argv[1]);
    perftest(f);
    return 0;
}

