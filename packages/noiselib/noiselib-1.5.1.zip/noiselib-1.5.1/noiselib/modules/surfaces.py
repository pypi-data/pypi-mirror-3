from __future__ import division
from numpy import asarray, ndarray, ndenumerate
from pygame import Surface
from pygame.surfarray import pixels2d



map_rgb = Surface((0, 0)).map_rgb

#   linear interpolation
#   a:  a float between 1 and 0 that determines the point of interpolation
#   p, q: the endpoints of the interpolation
def lerp(a, p, q): return tuple((_p + ((_q - _p) * a)) for _p, _q in zip(p, q)) #

def bilerp(a, p1, q1, p2, q2):
    a0, a1 = a[0], a[1]                                                         #
    p = lerp(a0, p1, q1)                                                        #
    q = lerp(a0, p2, q2)                                                        #
    return lerp(a1, p, q)                                                       #


################################################################################
# Color modules
class RGBLerpNoise(object):

    def __init__(self, colors, source):
        self.colors = colors
        self.source = source

    def __call__(self, coords):
        colors, source = self.colors, self.source
        colors, e = colors[0:2], colors[2]
        return map_rgb([int(v) for v in lerp(source(coords)**e, *colors)])


################################################################################
# Arrays
class PixelArray(ndarray):

    def __new__(cls, surface, source):
        pxarray = pixels2d(surface)
        pxarray = asarray(pxarray).view(cls)
        for i, e in ndenumerate(pxarray): pxarray[i] = source(i)
        return pxarray
