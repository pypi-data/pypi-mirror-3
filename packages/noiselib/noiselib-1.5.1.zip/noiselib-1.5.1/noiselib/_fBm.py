# Copyright (c) 2011, Chandler Armstrong (omni dot armstrong at gmail dot com)
# see LICENSE.txt for details



"""
fractal Brownian motion
"""



from __future__ import division



######################################################################
# Fractal Brownian Motion
class Main(object):
    """fractal Brownian motion"""

    def __init__(self, octaves, persistence, source, f=None):
        """
        octaves : the number of layers of noise
        persistence : per octave modifier for amplitude; a float
        lacunarity : per octave modifier for frequency (hardcoded at two; each
          octave is a power of two greater than the previous)
        source : source noise function of the following prototype:
          source(coords) where coords is a sequence of numbers
        f : modifier function of the following prototype:
          f(noise) where noise is a float
        """
        self.octaves = octaves
        _octaves_ = xrange(octaves)
        self._octaves_ = zip(reversed(_octaves_), _octaves_)
        self.persistence = persistence
        self.lacunarity = 2
        self.source = source
        if f: self.f = f
        else: self.f = lambda s: s # else: the identity function

    def __call__(self, coords):
        """
        return blended octaves of noise at coords
        coords must be a sequence of numbers
        """
        # return blended octaves of noise at coords scaled to [-1, 1]
        persistence, lacunarity = self.persistence, self.lacunarity
        source, _octaves_, f = self.source, self._octaves_, self.f
        amp_sum = 0
        total = 0
        for i, j in _octaves_:
            freq = lacunarity**-i
            amp = persistence**j
            noise = source([d * freq for d in coords])
            total += f(noise) * amp
            amp_sum += amp
        # divide the total by the sum of amplitudes (i.e. a weighted average)
        return total / amp_sum

    def set_key(self, i):
        octaves = self.octaves
        self._octaves_ = zip(reversed(xrange(octaves)), xrange(i, octaves + i))
