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
# Abstract filename: exoskelegram.data.init

import sys
import os
import re
import pickle

_regex = re.compile(r'^0x([0-9abcdef]{4})\s+U([0-9abcdef]{4})\s+.\s+# .+$')
_exodata_path = os.path.expanduser('~/.exoskelegram/data')
_exodata_keysyms_file = os.path.join(_exodata_path, 'keysyms.pickled')

def get_keysym_unicode_pairs(filename=None):
    if not filename:
        if os.path.exists(_exodata_keysyms_file):
            with open(_exodata_keysyms_file, 'rb') as f:
                try:
                    return pickle.load(f)
                except Exception:
                    pass
        filename = os.path.join(os.path.dirname(__file__), 'keysyms.txt')
    u2k, k2u = {}, {}
    with open(filename) as f:
        for line in f:
            m = _regex.match(line)
            if m:
                keysym, uni = (int(x, base=16) for x in m.groups())
                if not uni in u2k:
                    u2k[uni] = keysym
                    k2u[keysym] = uni
    data = u2k, k2u
    if not os.path.isdir(_exodata_path):
        os.makedirs(_exodata_path)
    with open(_exodata_keysyms_file, 'wb') as f:
        pickle.dump(data, f)
    return data
