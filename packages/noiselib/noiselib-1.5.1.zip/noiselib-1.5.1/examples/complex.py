import cProfile

import noiselib
from noiselib import fBm, simplex_noise2
from noiselib.callbacks import billow, Ridged
from noiselib.modules.main import BlendNoise, NoiseArray, RescaleNoise, ScaleBiasNoise
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
        source_0 = fBm(8, 0.5, simplex_noise2, f = billow)
        source_1 = fBm(11, 0.5, simplex_noise2, f = Ridged(11))
        # curry sources with modules
        # applying source_0 to the ScaleBiaseNoise module returns another source function
        source_0 = ScaleBiasNoise(0.125, -0.75, source_0)
        # applying source_0 and source_1 to BlendNoise module returns another source function
        source = BlendNoise(source_1, source_0, source_1)
        # rescale source
        source = RescaleNoise((-1, 1), (0, 1), source)
        # convert source data into rgb ints
        colors_0 = ((0, 0, 0), (255, 255, 255), 1)
        # applying source to the ColorNoise module returns a function mapping source data to rgb ints
        source = RGBLerpNoise(colors_0, source)
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
    cProfile.run('demo.start()')
