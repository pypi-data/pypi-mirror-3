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

##[ Name        ]## pebsaq.various
##[ Maintainer  ]## Niels G. W. Serup <ns@metanohi.name>
##[ Description ]## Various minor (but still important) parts

import sys
import subprocess
import pebsaq.generalinformation as ginfo
try:
    from termcolor import colored
except ImportError:
    from pebsaq.external.termcolor import colored

def error(msg, done=None, pre=None, **kwds):
    errstr = str(msg) + '\n'
    if pre is not None:
        errstr = pre + ': ' + errstr
    if kwds.get('use_color'):
        errstr = colored(errstr, 'red')
    sys.stderr.write(errstr)
    if done is not None:
        if done in (True, False):
            sys.exit(1)
        else:
            sys.exit(done)

def _usable_error(msg, done=None, **kwds):
    error(msg, done, ginfo.program_name + ': ', **kwds)

def status(msg, pre=None, **kwds):
    statstr = str(msg)
    if pre is not None:
        statstr = pre + statstr
    if kwds.get('use_color'):
        statstr = colored(statstr, 'blue')
    print statstr

def _usable_status(msg, **kwds):
    status(msg, ginfo.program_name + ': ', **kwds)
