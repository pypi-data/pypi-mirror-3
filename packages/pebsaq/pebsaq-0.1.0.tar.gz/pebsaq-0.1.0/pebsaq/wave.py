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

##[ Name        ]## pebsaq.wave
##[ Maintainer  ]## Niels G. W. Serup <ns@metanohi.name>
##[ Description ]## Contains basic waves

import math

class GenericWave(object):
    def __init__(self, synthesizer):
        self.synthesizer = synthesizer
        self.update()

    def update(self):
        pass

    def __call__(self, t):
        return self.generate(t)

    def generate(self, t):
        return 0

class SineWave(GenericWave):
    def update(self):
        self.constant = 2 * math.pi * self.synthesizer.frequency / float(self.synthesizer.frame_rate)
        
    def generate(self, t):
        return math.sin(self.constant * t)

class SquareWave(SineWave):
    def generate(self, t):
        return cmp(math.sin(self.constant * t), 0)

class TriangleWave(GenericWave):
    def update(self):
        self.rwidth = self.synthesizer.frame_rate / self.synthesizer.frequency / 4
        self.width = float(self.rwidth)
        
    def generate(self, t):
        t %= self.rwidth * 4
        if t <= self.width:
            return t / self.width
        elif self.width < t <= self.width * 2:
            return 1 - (t - self.width) / self.width
        elif self.width * 2 < t <= self.width * 3:
            return -(t - self.width * 2) / self.width
        elif self.width * 3 < t <= self.width * 4:
            return - 1 + (t - self.width * 3) / self.width

