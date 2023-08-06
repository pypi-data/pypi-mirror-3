from __future__ import division
from numpy import asarray, empty, ndarray, ndenumerate
from operator import mul



#   linear interpolation
#   a:  a float between 1 and 0 that determines the point of interpolation
#   p, q: the endpoints of the interpolation
def lerp(a, p, q): return tuple((_p + ((_q - _p) * a)) for _p, _q in zip(p, q)) #

def bilerp(a, p1, q1, p2, q2):
    a0, a1 = a[0], a[1]                                                         #
    p = lerp(a0, p1, q1)                                                        #
    q = lerp(a0, p2, q2)                                                        #
    return lerp(a1, p, q)                                                       #


def scurve3(x): return x * x * (3 - 2 * x)


def scale((xmin, xmax), (ymin, ymax), x): return (x * ((ymax - ymin) / (xmax - xmin))) + (((ymin * xmax) - (ymax * xmin)) / (xmax - xmin))


def prod(X): return reduce(mul, X)


################################################################################
# Uniform
class UniformNoise(object):
# return a uniform value.  simply a `dummy' for a noise function when a constant is desired
    def __init__(self, x):
        self.x

    def __call__(self, *a, **kw):
        return self.x


################################################################################
# Selector Modules
class _Selector(object):
# abstract base class for selector modules

    def __init__(self, control, source_0, source_1):
        self.control = control
        self.source_0 = source_0
        self.source_1 = source_1


class SelectNoise(_Selector):
# select from two source modules using a control module; blend within a given edge area
    def __init__(self, threshold, edge = 0, *a, **kw):
        _Selector.__init__(self, *a, **kw)
        self.threshold = threshold
        self.edge = edge

    def __call__(self, coords):
        edge, threshold = self.edge, self.threshold
        control, source_0, source_1 = self.control, self.source_0, self.source_1
        cval = control(coords)
        if cval < threshold - edge: return source_0(coords)
        elif cval < threshold + edge:
            l, u = threshold - edge, threshold + edge
            a = (cval - l) / (u - l)
            a, p, q = scurve3(a), source_0(coords), source_1(coords)
            return lerp(a, [p], [q])[0]
        else: return source_1(coords)


class BlendNoise(_Selector):
# lerp two source modules using a control module as alpha
    def __init__(self, *a, **kw):
        _Selector.__init__(self, *a, **kw)

    def __call__(self, coords):
        control, source_0, source_1 = self.control, self.source_0, self.source_1
        return lerp(control(coords), [source_0(coords)], [source_1(coords)])[0]


################################################################################
# Modifier Modules
class ClampNoise(object):
# clamp output of a noise producing module within a lower and upper bound
    def __init__(self, lowerbound, upperbound, source):
        self.lowerbound = lowerbound
        self.upperbound = upperbound
        self.source = source

    def __call__(self, coords):
        lowerbound, upperbound = self.lowerbound, self.upperbound
        source = self.source
        noise = source(coords)
        if noise <= lowerbound: return lowerbound
        elif noise >= upperbound: return upperbound
        return noise


class AbsNoise(object):
# take the absolute value of a noise producing module
    def __init__(self, source):
        self.source = source

    def __call__(self, coords):
        source = self.source
        return abs(source(coords))


class ExponentNoise(object):
# map noise producing module to an exponential curve

    def __init__(self, p, source):
        self.p = p
        self.source = source

    def __call__(self, coords):
        p, source = self.p, self.source
        return source(coords)**p


class CurveNoise(object):
# map noise producing module to an arbitrary curve
    def __init__(self, curve, source):
        self.curve = curve
        self.source = source

    def __call__(self, coords):
        curve, source = self.curve, self.source
        return curve(source(coords))


class InvertNoise(object):
# Invert a noise producing module
    def __init__(self, source):
        self.source = source

    def __call__(self, coords):
        source = self.source
        return source(coords) * -1


class ScaleBiasNoise(object):
# Scale and bias a noise producing module

    def __init__(self, scalar, bias, source):
        self.scalar = scalar
        self.bias = bias
        self.source = source

    def __call__(self, coords):
        scalar, bias, source = self.scalar, self.bias, self.source
        noise = source(coords) * scalar + bias
        if noise <= -1: return -1
        elif noise >= 1: return 1
        return noise

class RescaleNoise(object):

    def __init__(self, (xmin, xmax), (ymin, ymax), source):
        self.X = (xmin, xmax)
        self.Y = (ymin, ymax)
        self.source = source

    def __call__(self, coords):
        X, Y, source = self.X, self.Y, self.source
        return scale(X, Y, source(coords))


################################################################################
# Combiner modules
class AddNoise(object):
# sum the noise of a list of source modules

    def __init__(self, *a):
        self.sources = a

    def __call__(self, coords):
        sources = self.sources
        return sum([source(coords) for source in sources])


class MaxNoise(object):
# return the maximum value of a list of source modules
    def __init__(self, *a):
        self.sources = a

    def __call__(self, coords):
        sources = self.sources
        return max([source(coords) for source in sources]) 


class MinNoise(object):
# return the minimum value of a list of source modules
    def __init__(self, *a):
        self.sources = a

    def __call__(self, coords):
        sources = self.sources
        return min([source(coords) for source in sources])        


class MultNoise(object):
# take the product of a list of source modules

    def __init__(self, *a):
        self.sources = a

    def __call__(self, coords):
        sources = self.sources
        return prod([source(coords) for source in sources])


class PowerNoise(object):
# raise a source module to a control module
    def __init__(self, control, source):
        self.control = control
        self.source = source

    def __call__(self, coords):
        control, source = self.control, self.source
        return source(coords)**control(coords)


################################################################################
# Arrays
class NoiseArray(ndarray):
#   noise cached into an array

    def __new__(cls, shape, source):
        A = empty(shape).view(cls)
        for i, e in ndenumerate(A):
            A[i] = source(i)
        return A

    def __call__(self, coords):
        return self[coords]
