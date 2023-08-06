#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pebsaq: a poor synthesizer
# Copyright (C) 2010, 2012  Niels G. W. Serup

# This file is part of pebsaq.
#
# pebsaq is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pebsaq is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pebsaq.  If not, see <http://www.gnu.org/licenses/>.

##[ Name        ]## pebsaq.drawwave
##[ Maintainer  ]## Niels G. W. Serup <ns@metanohi.name>
##[ Description ]## Draws waves

import pygame
from pygame.locals import *

class WaveDrawer(object):
    def __init__(self, width=320, height=240):
        self.width = width
        self.height = height
        self.points = []

    def add_point(self, x):
        self.points.append((-x * 0.99 + 1) * self.height / 2)

    def start(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('pebsaq wave')

        self.bg_fill = pygame.Surface(self.screen.get_size()).convert()
        self.bg_fill.fill((255, 255, 255))
        self.dot = pygame.Surface((1, 1)).convert()
        self.dot.fill((0, 0, 0))

    def check_for_input(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key in (K_3, K_KP3):
                    return 'freq', -10
                elif event.key in (K_6, K_KP6):
                    return 'freq', +10
                if event.key in (K_DOWN,):
                    return 'amp', -0.1
                elif event.key in (K_UP,):
                    return 'amp', +0.1
                elif event.key in (K_1, K_KP1):
                    return 'sin', -1
                elif event.key in (K_2, K_KP2):
                    return 'sin', +1
                elif event.key in (K_4, K_KP4):
                    return 'sqr', -1
                elif event.key in (K_5, K_KP5):
                    return 'sqr', +1
                elif event.key in (K_7, K_KP7):
                    return 'tri', -1
                elif event.key in (K_8, K_KP8):
                    return 'tri', +1
                elif event.key in (K_0, K_KP0, K_m):
                    return 'mute', None
                elif event.key == K_ESCAPE:
                    return 'exit', None
            elif event.type == QUIT:
                return 'exit', None
        return None, None

    def draw(self):
        ratio = self.width / float(len(self.points))
        self.screen.blit(self.bg_fill, (0, 0))
        i = 0.0
        ppos = [0, self.points[0]]
        for x in self.points:
            cpos = [i, x]
            pygame.draw.aaline(self.screen, (0, 0, 0), ppos, cpos)
            ppos = cpos
            i += ratio
        self.points = []
        pygame.display.flip()
