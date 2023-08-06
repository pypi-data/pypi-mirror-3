#!/usr/bin/env python

# qvikconfig: read and write simple config files
# Copyright (C) 2010  Niels Serup

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Version:...... 0.1.0
# Maintainer:... Niels Serup <ns@metanohi.org>
# Website:...... http://metanohi.org/projects/qvikconfig/
# Development:.. http://gitorious.org/qvikconfig

# This is a Python module. It reads and writes simple documentation
# files. The basic syntax is 'property = value'. Documentation is
# included in this very file.

# Imports
import re
import decimal # For floats which would otherwise lose information

# Documentation
__doc__ = """
==========
qvikconfig
==========

qvikconfig is a parser of a simple config file syntax called the
qvikconfig format. The basic syntax is 'property = value'.

qvikconfig offers two main functions: ``parse`` and ``dump``. Use
``parse`` to read config files and ``dump`` to write them.

Documentation
=============

To see an example of qvikconfig config files and how to parse and dump
them, see the files in the ``tests/`` directory of the
distribution. Alternatively, these examples can be downloaded from
<http://metanohi.org/projects/qvikconfig/>.

qvikconfig can be considered a dictionary that can link both single
values and lists of values to named properties. Entries are
line-separated. A simple example::

  # This is a comment.
  name = Example # This is also a comment.
  descriptions = This is an example, Dette er et eksempel

When parsed, this will be translated to this Python dict:

  {'name': 'Example',
  'descriptions': ['This is an example', 'Dette er et eksempel']}

It is, in most cases, optional to enclose strings in
quotes. Whitespace is completely optional.


Lists
-----

qvikconfig uses the comma character to split values, as seen in the
example above. When there is only one value associated with a
property, there will be no list. Otherwise there will be one. To
create a list of only one value, append two commas to your value, like
this::

  a-list=24,,

This returns this dict::

  {'a-list': [24]}


Accepted data
-------------

qvikconfig accepts and understands strings, numbers, True, False, and
None. Everything else normally results in unknown behavior.

Strings are represented using text, sometimes enclosed in
quotes. Numbers are represented using numbers. True, False and None
are represented by true, false and none.


Using more than one line
------------------------

You can spread lists across several lines like this::

  long list = A,
  B, C, D,
  E, F, G,
  H, I, J,
  K, L, M,
  N, P, O

This will, naturally, result in this dict::

  {'long list': ['A', 'B', 'C', 'D', 'E', 'F',
  'G', 'H','I', 'J', 'K', 'L', 'M', 'N', 'P', 'O']}

You can make single values take up more than one line like this::

  a value = The wall had moved away from the boundaries \
of the house.

..which creates this when parsed::

  {'a value': 'The wall had moved away from the boundaries of the house.'}


Escaping text
-------------

Certain strings cannot be represented in qvikconfig config files
without being enclosed in quotes. The strings 'true', 'false' and
'none' must have quotes (both "..." and '...' are accepted), for
example. The same goes for, in the case of values, strings containing
commas and quotes or ending with a backslash, and in the case of
properties, equal signs. While spaces and tabs are just fine, newlines
(and carriage returns and so on) must be enclosed in quotes. Example::

  # The equality sign is not a comma.
  '=' = 'not a ,'

..resulting in::

  {'=': 'not a ,'}


Version information
-------------------

This is version 0.1.0 of qvikconfig. New releases are made available
online at the website mentioned earlier.

Copyright (C) 2010  Niels Serup
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


# Constants
_config_comment_regex = re.compile(r'#.*')

# The parser class
class _QvikParser(dict):
    def __init__(self, in_file=None, **kwargs):
        # Try to find out if input is a file or a string. If it's a
        # file, extract the data.
        
        def fil2dat(t):
            # If it's a file..
            try:
                return open(t, 'U').read()
            except TypeError:
                try:
                    return t.read().replace(
                        '\r\n', '\n').replace('\r', '\n')
                except Exception:
                    raise TypeError('argument not file')

        # Testing
        fil = kwargs.get('file')
        if not fil:
            dat = kwargs.get('data')
            if not dat:
                if in_file:
                    fil = in_file
                    dat = fil2dat(fil)
                else:
                    raise TypeError('missing arguments')
            else:
                if not isinstance(dat, basestring):
                    raise TypeError('data must be a string')
        else:
            dat = fil2dat(fil)

        # Save the data in case someone needs it
        self.rawdata = dat
        # Parse
        self.parse_data()

    def convert(self, dat):
        # Convert to internal Python data
        if dat.startswith('"') or dat.startswith("'"):
            return eval(dat)
        if dat == 'true':
            return True
        if dat == 'false':
            return False
        if dat == 'none':
            return None
        try:
            return int(dat)
        except ValueError:
            try:
                return decimal.Decimal(dat)
            except decimal.InvalidOperation:
                return dat

    def parse_data(self):
        # Parse the rawdata string
        data = _config_comment_regex.sub('', self.rawdata).split('\n')
        data.append('')

        for i in range(len(data) - 1):
            # All entries have one property and one or more values.
            x = data[i].strip()
            if not x: continue
            t = i
            comma = x.endswith(',') and not x.endswith(',,')
            while comma or x.endswith('\\'):
                t += 1
                if comma:
                    x += data[t].strip()
                else:
                    x = x[:-1] + data[t]
                data[t] = ''
                comma = x.endswith(',')

            prop = None
            for qtype in ('"', "'"):
                if x.startswith(qtype):
                    offset = 1
                    while True:
                        tn = x.find(qtype, offset)
                        try:
                            new_search_cond = x[tn - 1] == '\\' \
                                and x[tn - 2] != '\\'
                        except IndexError:
                            new_search_cond = False
                        if tn == -1:
                            raise SyntaxError('missing end quote \
in entry beginning on line %d' % (i + 1))
                        elif new_search_cond:
                            offset = tn + 1
                        else:
                            prop = self.convert(x[:tn + 1])
                            cval = x[tn + 1:].strip()
                            if not cval.startswith('='):
                                raise SyntaxError('no equal sign \
present in entry beginning on line %d' % (i + 1))
                            else:
                                cval = cval[1:].lstrip()
                            break

            if not prop:
                tn = x.find('=')
                prop = x[:tn].rstrip()
                cval = x[tn + 1:].strip()
            vals = []
            done = False
            while not done:
                halfdone = False
                for qtype in ('"', "'"):
                    if cval.startswith(qtype):
                        offset = 1
                        while True:
                            tn = cval.find(qtype, offset)
                            try:
                                new_search_cond = cval[tn - 1] == '\\' \
                                    and cval[tn - 2] != '\\'
                            except IndexError:
                                new_search_cond = False
                            if tn == -1:
                                raise SyntaxError('missing end quote \
in entry beginning on line %d' % (i + 1))
                            elif new_search_cond:
                                offset = tn + 1
                            else:
                                break
                        vals.append(self.convert(cval[:tn + 1]))
                        cval = cval[tn + 1:].lstrip()
                        if cval.startswith(','):
                            cval = cval[1:].lstrip()
                            halfdone = True
                            break
                        else:
                            done = True
                            break
                if done: break
                elif halfdone: continue
                # If not with quotes
                end = cval.find(',')
                if end != -1:
                    vals.append(self.convert(cval[:end].rstrip()))
                    cval = cval[end + 1:].lstrip()
                else:
                    vals.append(self.convert(cval.rstrip()))
                    break
            if len(vals) == 1:
                vals = vals[0]
            else:
                nvals = []
                for x in vals:
                    if x != '': nvals.append(x)
                vals = nvals
            self.__setitem__(prop, vals)
            

###############
## FUNCTIONS ##
###############

# Parsing (reading)
#~~~~~~~~~~~~~~~~~~
def parse(in_file=None, **kwargs):
    """
    parse([filename|file_object], (file=filename|file_object)|data=string)
    
    Parse simple config files adhering to the qvikconfig format. The
    basic syntax is 'property = value'. Executing help(qvikconfig)
    will reveal the complete documentation.
    """
    class QvikParser(_QvikParser): pass
    return QvikParser(in_file, **kwargs)

# Dumping (writing)
#~~~~~~~~~~~~~~~~~~
# Disallowed characters and patterns in strings not using
# quotes. Newlines and others must be put inside quotes, but spaces
# and tabs are okay.
_bads_general = '\n\r\a\f\b\v' + chr(0x15)
_bads_prop = _bads_general + '='    # For properties
_bads_vals = _bads_general + ',"\'' # For values
_bads_vals_regexes = [
    re.compile(r'^.*?\\$'),
    re.compile(r'^none|true|false$')
    ]

def _convert_back(dat, bads, regexes=None):
    # Convert a piece of internal Python data to a string matching the
    # rules of the qvikconfig format
    if dat is None:
        return 'none'
    if dat is True:
        return 'true'
    if dat is False:
        return 'false'
    if isinstance(dat, basestring):
        # Quote the string if it contains forbidden letters or patterns
        ok = True
        for l in dat:
            if l in bads:
                ok = False
                break
        if ok and regexes:
            for x in regexes:
                if x.match(dat):
                    ok = False
                    break
        if ok:
            return dat
        else:
            return repr(dat)
    # Else
    return str(dat) # ints and the like

def _yield_dump(in_dict):
    # Dump dict data one entry at a time
    for o_prop, o_vals in in_dict.iteritems():
        if not isinstance(o_prop, basestring):
            raise TypeError('identifiers must be strings')
        prop = _convert_back(o_prop, _bads_prop)
        if isinstance(o_vals, list):
            vals = ''
            for x in o_vals:
                vals += _convert_back(x, _bads_vals, _bads_vals_regexes) + ', '
            vals = vals[:-2]
            if len(o_vals) == 1:
                vals += ',,'
        else:
            vals = _convert_back(o_vals, _bads_vals, _bads_vals_regexes)
        yield '%s = %s\n' % (prop, vals)

def dump(in_dict, out_file=None):
    """
    dump(dict[, outfile])
    
    Translate a dict to the qvikconfig syntax. If no outfile is given,
    the output will be returned as a string.
    """
    if out_file:
        for x in _yield_dump(in_dict):
            out_file.write(x)
        return True
    else:
        newdata = ''
        for x in _yield_dump(in_dict):
            newdata += x
        return newdata
