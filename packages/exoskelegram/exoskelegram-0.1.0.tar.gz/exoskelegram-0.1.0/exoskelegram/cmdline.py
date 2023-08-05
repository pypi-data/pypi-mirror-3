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
# Abstract filename: exoskelegram.cmdline

import sys
import os
from optparse import OptionParser
import exoskelegram
from . import xkeylib

def _catch_and_print(lock=False, stopkeysym=None):
    def thinkstart(stopkeysym):
        def think(keycode, keysym, pressed):
            print(' pressed' if pressed else 'released', 'keycode:', keycode,
                  'keysym:', keysym)
            if pressed and keysym == stopkeysym:
                return True
        xkeylib.get_key_events(think, lock)

    if stopkeysym is None:
        class C:
            pass
        c = C()
        print('Press key for stopping the key events catching.')
        def getkeysym(keycode, keysym, pressed):
            if pressed:
                c.sym = keysym
                print('Key pressed. Now catching.')
                return True
        xkeylib.get_key_events(getkeysym, lock)
        thinkstart(c.sym)
    else:
        thinkstart(stopkeysym)

def parse_args(cmdargs=None):
    """Generate an image based on command-line arguments."""
    class _SimplerOptionParser(OptionParser):
        """A simplified OptionParser"""

        def format_description(self, formatter):
            self.description = self.description.strip()
            return OptionParser.format_description(self, formatter)

        def format_epilog(self, formatter):
            return self.epilog

        def add_option(self, *args, **kwds):
            try: kwds['help'] = kwds['help'].strip()
            except KeyError: pass
            return OptionParser.add_option(self, *args, **kwds)

    parser = _SimplerOptionParser(prog= 'exoskelegram',
                              usage= 'Usage: exoskelegram COMMAND [ARGS...]',
                              version=exoskelegram.__copyright__, description= '''
An X11 key press/release catcher/sender wrapper with abstractions
''', epilog= '''
Commands (note: [<arg>?<default>] means that <arg> is a boolean value where t is
true and f is false):

  catch [lock?f] [stopkeysym]
    Catch all X key events and print them to standard out. If lock is true,
    take control of all the events and don't let them get further than to this
    program. If stopkeysym is specified, stop catching when that keysym is
    caught. If it is not specified, have the user press the corresponding key
    before starting the catch loop.

  mapkey keycode keysym [shift_keysym[ mode_switch_keysym[ both_keysym]]]
    Map a key at keycode to the keysyms specified. If only one keysym is
    specified, the key is an alias to that keysym with and without any
    modifiers. If shift_keysym is given, Shift+key will invoke that keysym. If
    mode_switch_keysym is given, Mode_Switch (sometimes called AltGr or Option)
    + key will invoke that keysym. If both_keysym is given,
    Shift+Mode_Switch+key will invoke that keysym. If a keysym is given for one
    modifier but not for the rest, it will also be used for the other modifiers.

  sendkey keycode [press?t] [release?t]
    Send a key to the global X server. If press, send a key press. If release,
    send a key release. If both, first press, then release.

  sendtext text
    Send a text string to the X server (a series of press-release of keys).

  symtocode keysym
    Convert a keysym to a keycode and print.

  codetosym keycode
    Convert a keycode to its corresponding four keysyms and print.

  nametosym name
    Convert an XString to a keysym and print.

  symtouni keysym
    Convert a keysym to a unicode character and print.

  unitosym unicodechar
    Convert a unicode character to a keysym and print.

  xflush
    Flush the X server.


Examples:
  exoskelegram catch f 65307
    Catch key events, do not lock, end on ESC press.

  exoskelegram mapkey 23 121
    Map the key at keycode 23 to the letter 'y'.

  exoskelegram sendkey 33
    Send the key at keysym 33 ('!').

  exoskelegram sendtext Hello
    Succesively send the characters H, e, l, l, and o.

  exoskelegram symtocode 89
    Prints the current keycode for the keysym 89.

  exoskelegram codetosym 28
    Prints the current keysyms for the keycode 28.

  exoskelegram nametosym asciitilde
    Prints the keysym for asciitilde

  exoskelegram symtouni 33
    Prints the unicode character of the keysym 33.

  exoskelegram unitosym Å
    Prints the keysym for the 'Å' letter.
''')

    if not cmdargs: cmdargs = sys.argv[1:]
    o, a = parser.parse_args(cmdargs)

    if len(a) < 1:
        parser.error('missing command')

    eq = lambda x: x
    boolf = lambda x: True if x == 't' else False
    boolt = lambda x: False if x == 'f' else True
    prt = lambda f: lambda *xs: print(f(*xs))
    cmds = {
        'catch': [[], [boolf, int], _catch_and_print],
        'mapkey': [[int, int], [int, int, int], lambda kc, *ks: xkeylib.map_key(kc, ks)],
        'sendkey': [[int], [boolt, boolt], xkeylib.send_keysym],
        'sendtext': [[eq], [], xkeylib.send_text],
        'symtocode': [[int], [], prt(xkeylib.keysym_to_keycode)],
        'codetosym': [[int], [], prt(xkeylib.keycode_to_keysyms)],
        'nametosym': [[eq], [], prt(xkeylib.name_to_keysym)],
        'symtouni': [[int], [], prt(lambda *xs: chr(xkeylib.keysym_to_unicode(*xs)))],
        'unitosym': [[ord], [], prt(xkeylib.unicode_to_keysym)],
        'xflush': [[], [], xkeylib.xflush],
        'help': [[], [], parser.print_help]
        }

    cmd = a[0]
    del a[0]
    try:
        cargs = cmds[cmd]
    except KeyError:
        parser.error('command does not exist')
    args = cargs[0]
    func = cargs[2]
    if len(a) < len(args):
        parser.error('not enough arguments')
    for i in range(len(a) - len(args)):
        try:
            args.append(cargs[1][0])
        except IndexError:
            break
        del cargs[1][0]
    try:
        args = tuple(map(lambda i: args[i](a[i]), range(len(args))))
    except ValueError:
        parser.error('wrong type')
    func(*args)
  
if __name__ == '__main__':
    parse_args()
