#!/usr/bin/env python3

import sys
import os

import exoskelegram.xkeylib as xkeylib

class Runner:
    def __init__(self):
        pass
    
    def run(self):
        xkeylib.get_key_events(self.think, False)
        # xkeylib.get_key_events(self.think, False, lambda: print('Done.'))

    def think(self, keycode, keysym, pressed):
        print('pressed' if pressed else 'released', 'keycode:', keycode,
              'keysym:', keysym)
        if keysym == 0x20: # space
            return True

    def end(self):
        pass

if __name__ == '__main__':
    r = Runner()
    r.run()
