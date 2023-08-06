from math import cos, pi, sin

import noiselib
from noiselib import fBm, simplex_noise3
from noiselib.modules.main import RescaleNoise
from noiselib.modules.surfaces import PixelArray, RGBLerpNoise
import pygame
from pygame import display, draw, Surface
from pygame.locals import *
################################################################################
noiselib.init(128)


TWOPI = 2 * pi

SCREEN_SIZE = (800, 600)
SCREEN = display.set_mode(SCREEN_SIZE)
TILE_SIZE = tuple(2 * [int(TWOPI * 50)])


class Torus(object):

    def __init__(self, r, R):
        self.r = r
        self.R = R

    def __call__(self, (u, v)):
        r, R = self.r, self.R
        x = (R + r * cos(v)) * cos(u)
        y = (R + r * cos(v)) * sin(u)
        z = r * sin(v)
        return x, y, z


class TorusNoise(object):

    def __init__(self, noise3, torus):
        self.noise3 = noise3
        self.torus = torus

    def __call__(self, (u, v)):# u, v must be 0 < u/v < 2pi
        u = (u / 50.0) % TWOPI
        v = (v / 50.0) % TWOPI
        x, y, z = self.torus((u, v))
        r = self.noise3((x, y, z))
        return r


class Demo(object):

    def start(self):
        source = fBm(8, 0.5, simplex_noise3)
        r, R = 32, 128 # variety in nosie is a function of surface size
        torus = Torus(r, R)
        source = TorusNoise(source, torus)
        # noise must be in [0, 1] for RGB
        source = RescaleNoise((-1, 1), (0, 1), source)
        colors = ((77, 61, 43), (255, 205, 143), 1)
        # applying source to the ColorNoise module returns a function mapping source data to rgb ints
        source = RGBLerpNoise(colors, source)
        # initialize surface and pixel array
        surface = Surface(SCREEN_SIZE)
        # read rgb ints into pixel array
        pxarray = PixelArray(surface, source)
        # blit surface
        del pxarray
        SCREEN.blit(surface, (0, 0))
        draw.rect(SCREEN, (255, 0, 0), Rect((80, 60), TILE_SIZE), 2)
        pygame.display.flip()
        while 1:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_q: exit()


if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        print 'psyco unavailable'
        pass
    pygame.init()
    demo = Demo()
    demo.start()
