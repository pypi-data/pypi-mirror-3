import noiselib
from noiselib import fBm, simplex_noise2
from noiselib.modules.main import RescaleNoise
from noiselib.modules.surfaces import PixelArray, RGBLerpNoise
import pygame
from pygame import Surface
from pygame import display
from pygame.locals import *
################################################################################
noiselib.init(256)


SCREEN_SIZE = (800, 600)
SCREEN = display.set_mode(SCREEN_SIZE)


class Demo(object):

    def start(self):
        # initialize sources
        source = fBm(8, 0.5, simplex_noise2)
        # rescale source for RGB
        source = RescaleNoise((-1, 1), (0, 1), source)
        # convert source data into rgb ints
        colors = ((0, 0, 0), (255, 255, 255), 1)
        # applying source to the ColorNoise module returns a function mapping source data to rgb ints
        source = RGBLerpNoise(colors, source)
        # initialize surface and pixel array
        surface = Surface(SCREEN_SIZE)
        # read rgb ints into pixel array
        pxarray = PixelArray(surface, source)
        # blit surface
        del pxarray
        SCREEN.blit(surface, (0, 0))
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
