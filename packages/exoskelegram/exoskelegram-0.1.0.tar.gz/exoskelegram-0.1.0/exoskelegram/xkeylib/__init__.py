#!/usr/bin/env python3

# exoskelegram: An X11 key press/release catcher/sender wrapper
# Copyright (C) 2011 Niels Serup

# This file is part of exoskelegram.

# exoskelegram is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.

# exoskelegram is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.

# You should have received a copy of the GNU Affero General Public License
# along with exoskelegram.  If not, see <http://www.gnu.org/licenses/>.

# Maintainer: Niels Serup <ns@metanohi.name>
# Abstract filename: exoskelegram.xkeylib.init

import sys
import os
from ._xlib import get_key_events, map_key, xflush, send_keycode, \
    keysym_to_keycode, keycode_to_keysyms, name_to_keysym
from exoskelegram.data import get_keysym_unicode_pairs

PLACEHOLDERKEYCODE = 8 # Is anyone using this?

_selfdict = sys.modules[__name__].__dict__
_initedfuncs = []
def _reqinit(initfunc):
    '''Decorator for forcing initfunc to be run before running a function.'''
    def reqfunc(func):
        access_name = func.__name__[1:] # without the '_'
        def _funcwithinit(*args, **kwds):
            if not initfunc in _initedfuncs:
                initfunc()
                _initedfuncs.append(initfunc)
            _selfdict[access_name] = func
            _selfdict[access_name].__doc__ = func.__doc__
            return func(*args, **kwds)
        _funcwithinit.__doc__ = func.__doc__
        _selfdict[access_name] = _funcwithinit
        return func
    return reqfunc

def _init_keysym_unicode():
    global _k2u, _u2k
    _u2k, _k2u = get_keysym_unicode_pairs()

@_reqinit(_init_keysym_unicode)
def _keysym_to_unicode(keysym):
    '''keysym_to_unicode(keysym) -> unicode'''
    return _k2u[keysym]

@_reqinit(_init_keysym_unicode)
def _unicode_to_keysym(uni):
    '''unicode_to_keysym(unicode) -> keysym'''
    if isinstance(uni, str):
        uni = ord(uni)
    return _u2k[uni]

def send_keysyms(keysyms, press=True, release=True):
    '''Send keysyms.'''
    oldkeysyms = keycode_to_keysyms(PLACEHOLDERKEYCODE)
    for keysym in keysyms:
        map_key(PLACEHOLDERKEYCODE, [keysym])
        if press:
            send_keycode(PLACEHOLDERKEYCODE, True)
            xflush()
        else:
            release = True
        if release:
            send_keycode(PLACEHOLDERKEYCODE, False)
            xflush()
    # Map it back.
    map_key(PLACEHOLDERKEYCODE, oldkeysyms)

def send_keysym(keysym, press=True, release=True):
    '''Send a keysym.'''
    return send_keysyms([keysym], press, release)

def send_text(text):
    '''
    Repeatedly press and release the keys for with the characters in the text
    string.
    '''
    return send_keysyms(map(unicode_to_keysym, text))

