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

##[ Name        ]## pebsaq.synthesizer
##[ Maintainer  ]## Niels G. W. Serup <ns@metanohi.name>
##[ Description ]## Contains the synthesizer core

import alsaaudio
import time
import struct
import numpy
import pebsaq.wave as waves

class Synthesizer(object):
    def __init__(self, channels=1, sample_size=2, frame_rate=44100,
                 frequency=220, amplitude=0.5,
                 sin_str=1, sqr_str=1, tri_str=1,
                 cache_length=None, mute=False, interactive=True):
        self.channels = channels
        self.sample_size = sample_size
        self.frame_rate = frame_rate
        self.frequency = frequency
        self.amplitude = amplitude
        if abs(self.amplitude) > 1:
            self.amplitude = 1 * cmp(self.amplitude, 0)
        self.period_size = self.frame_rate / self.frequency
        self.frame_size = self.channels * self.sample_size
        self.pcm = None

        self.sin_strength = sin_str
        self.sqr_strength = sqr_str
        self.tri_strength = tri_str

        self.cache_length = cache_length
        self.mute = mute
        self.interactive = interactive

        if self.interactive:
            import pebsaq.drawwave as drawwave
            self.wave_drawer = drawwave.WaveDrawer()

    def load_wave(self, AWave):
        return AWave(self)
        
    def start(self):
        self.create_pcm()
        if self.cache_length:
            self.pcm.setperiodsize(self.cache_length)
        else:
            self.pcm.setperiodsize(self.period_size)
        self.calculate_period_in_seconds()

        self.sin = self.load_wave(waves.SineWave)
        self.sqr = self.load_wave(waves.SquareWave)
        self.tri = self.load_wave(waves.TriangleWave)

        if self.interactive:
            self.wave_drawer.start()

        self.run()

    def create_pcm(self):
        self.pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL)
        self.pcm.setchannels(self.channels)
        if self.sample_size == 2:
            self.pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            self.quantize = lambda f: struct.pack('<h', int(f * 32267))
        elif self.sample_size == 1:
            self.pcm.setformat(alsaaudio.PCM_FORMAT_U8)
            self.quantize = lambda f: struct.pack('B', int(f + 1) * 127)
        self.pcm.setrate(self.frame_rate)

    def delete_pcm(self):
        pcm = self.pcm
        self.pcm = None
        del pcm

    def set_period_size(self, samples):
        self.period_size = samples
        if not self.cache_length:
            try:
                self.pcm.setperiodsize(self.period_size)
            except alsaaudio.ALSAAudioError:
                reload(alsaaudio)
                self.delete_pcm()
                self.create_pcm()
                self.pcm.setperiodsize(self.period_size)
        self.calculate_period_in_seconds()

    def calculate_period_in_seconds(self):
        self.period_in_seconds = float(self.period_size) / \
            self.frame_rate
        if self.cache_length:
            self.cache_in_seconds = float(self.cache_length) / \
                self.frame_rate
            self.block_time = self.cache_in_seconds
        else:
            self.block_time = self.period_in_seconds

    def set_frequency(self, freq):
        self.frequency += freq
        self.set_period_size(self.frame_rate / self.frequency)
        self.sin.update()
        self.sqr.update()
        self.tri.update()
        self.generate_period()

    def set_amplitude(self, amp):
        self.amplitude += amp
        if abs(self.amplitude) > 1:
            self.amplitude = 1 * cmp(self.amplitude, 0)
        self.generate_period()

    def set_strength(self, wave, val):
        if wave == 'sin':
            self.sin_strength += val
            if self.sin_strength < 0:
                self.sin_strength = 0
        elif wave == 'sqr':
            self.sqr_strength += val
            if self.sqr_strength < 0:
                self.sqr_strength = 0
        elif wave == 'tri':
            self.tri_strength += val
            if self.tri_strength < 0:
                self.tri_strength = 0

        self.generate_period()

    def get_wave_data(self):
        strength = (self.sin_strength + self.sqr_strength +
                    self.tri_strength)
        for t in xrange(self.period_size):
            try:
                sin = self.sin.generate(t) * self.sin_strength
                sqr = self.sqr.generate(t) * self.sqr_strength
                tri = self.tri.generate(t) * self.tri_strength
                wave = (sin + sqr + tri) / strength
            except ZeroDivisionError:
                wave = 0
            t += 1
            yield wave * self.amplitude

    def generate_period(self):
        wave_data = numpy.empty(self.frame_size * self.period_size, dtype='uint8')

        i = 0
        if self.interactive:
            for x in self.get_wave_data():
                for y in self.quantize(x) * self.channels:
                    wave_data[i] = ord(y)
                    i += 1
                self.wave_drawer.add_point(x)
        else:
            for x in self.get_wave_data():
                for y in self.quantize(x) * self.channels:
                    wave_data[i] = ord(y)
                    i += 1

        wave_data = wave_data.tostring()
        self.wave_data = wave_data
        if self.cache_length:
            self.wave_data = wave_data[:]
            req_len = self.period_size + self.cache_length
            while len(self.wave_data) < req_len:
                self.wave_data += wave_data
            self.wave_data = self.wave_data[:req_len]
        self.wave_data_length = len(self.wave_data)
        if self.interactive:
            self.wave_drawer.draw()

    def run(self):
        self.generate_period()
        if self.cache_length:
            cache_use = True
            cache_len = self.cache_length
            cache_pos = 0
        else:
            cache_use = False
        done = False
        while not done:
            if not self.mute:
                if cache_use:
                    data = self.wave_data[cache_pos:cache_pos +
                                          cache_len]
                    # This does not work very well.
                    # print '%3d %3d %3d %3d' % (cache_pos, len(data),
                    #                        self.period_size, self.wave_data_length)
                    self.pcm.write(data)
                    cache_pos = (cache_pos + cache_len) % self.period_size
                else:
                    self.pcm.write(self.wave_data)
            else:
                time.sleep(self.block_time)
            if self.interactive:
                cmd, val = self.wave_drawer.check_for_input()
                if cmd == 'freq':
                    self.set_frequency(val)
                    cache_pos = 0
                elif cmd == 'amp':
                    self.set_amplitude(val)
                elif cmd in ('sin', 'sqr', 'tri'):
                    self.set_strength(cmd, val)
                elif cmd == 'mute':
                    self.mute = not self.mute
                elif cmd == 'exit':
                    done = True
