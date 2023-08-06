# Copyright (c) 2011, Chandler Armstrong (omni dot armstrong at gmail dot com)
# see LICENSE.txt for details



"""
noise modification functions
"""



def billow(s): return 2 * abs(s) - 1



class Ridged(object):


    def __init__(self, octaves):
        self._weight = 1
        self._octave = 0
        self.octaves = octaves


    def __call__(self, s):
        # ridged multifractal noise [0, 1]
        if self._octave == self.octaves:
            self._weight = 1
            self._octave = 0

        weight = self._weight
        offset = 1
        gain = 2
        s = (1 - abs(s))**2 * weight
        weight = s * gain
        if weight > 1: weight = 1
        elif weight < 0: weight = 0

        self._weight = weight
        self._octave += 1

        return s
