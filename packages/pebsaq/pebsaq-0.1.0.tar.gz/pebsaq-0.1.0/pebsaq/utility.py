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

##[ Name        ]## pebsaq.utility
##[ Maintainer  ]## Niels G. W. Serup <ns@metanohi.name>
##[ Description ]## Controls the actions of the command-line utility

import os
from pebsaq.settingsparser import SettingsParser
import pebsaq.various as various
import pebsaq.generalinformation as ginfo
import pebsaq.synthesizer as synthesizer

_config_file_translations = {
    'interactive': 'interactive',
    'frequency': 'frequency',
    'amplitude': 'amplitude',
    'channels': 'channels',
    'sample size': 'sample_size',
    'frame rate': 'frame_rate',
    'sine strength': 'sine_strength',
    'square strength': 'square_strength',
    'triangle strength': 'triangle_strength',
    'mute': 'mute',
    'cache length': 'cache_length',
    'verbose': 'term_verbose',
    'colored text': 'term_colored_text'
}

class Utility(SettingsParser):
    def __init__(self, **options):
        SettingsParser.__init__(self, _config_file_translations,
                                **options)
        # Get values, or set them to default ones
        self.set_if_nil('error_function', various._usable_error)
        self.set_if_nil('status_function', various._usable_status)
        self.set_if_nil('interactive', True)
        self.set_if_nil('frequency', 220)
        self.set_if_nil('amplitude', 0.5)
        self.set_if_nil('channels', 1)
        self.set_if_nil('sample_size', 2)
        self.set_if_nil('frame_rate', 44100)
        self.set_if_nil('sine_strength', 1)
        self.set_if_nil('square_strength', 1)
        self.set_if_nil('triangle_strength', 1)
        self.set_if_nil('mute', False)
        self.set_if_nil('cache_length', None)
        self.set_if_nil('term_verbose', True)
        self.set_if_nil('term_colored_text', True)
        self.set_if_nil('config_file_path',
                        os.path.expanduser('~/pebsaq.conf'))

        self.synthesizer = synthesizer.Synthesizer(
            self.channels, self.sample_size, self.frame_rate,
            self.frequency, self.amplitude, self.sine_strength,
            self.square_strength, self.triangle_strength,
            self.cache_length, self.mute, self.interactive)

    def error(self, msg, done=None):
        if self.term_verbose:
            self.error_function(msg, done, use_color=self.term_colored_text)

    def status(self, msg):
        if self.term_verbose:
            self.status_function(msg, use_color=self.term_colored_text)

    def start(self):
        self.synthesizer.start()

    def end(self):
        pass
