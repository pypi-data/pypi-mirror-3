/* exoskelegram: An X11 key press/release catcher/sender wrapper
 * Copyright (C) 2011 Niels Serup

 * This file is part of exoskelegram.

 * exoskelegram is free software: you can redistribute it and/or modify it under
 * the terms of the GNU Affero General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your option) any
 * later version.

 * exoskelegram is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
 * details.

 * You should have received a copy of the GNU Affero General Public License
 * along with exoskelegram.  If not, see <http://www.gnu.org/licenses/>.

 * Maintainer: Niels Serup <ns@metanohi.name>
 * Abstract filename: exoskelegram.xkeylib.xmisc.c
 */

#include "xmisc.h"

void xmisc_xflush(void) {
    XFlush(common_local_display);
}

KeyCode xmisc_keysym_to_keycode(KeySym keysym) {
    return XKeysymToKeycode(common_local_display, keysym);
}

KeysymList* xmisc_keycode_to_keysyms(KeyCode keycode) {
    int i;
    KeysymList* ks = (KeysymList*) malloc(sizeof(KeysymList));
    if (ks == NULL)
        exit(EXIT_FAILURE);
    
    for (i = 0; i < 4; i++) {
        ks->keysyms[i] = XKeycodeToKeysym(common_local_display, keycode, i);
    }
    return ks;
}

KeySym xmisc_string_to_keysym(char* s) {
    return XStringToKeysym(s);
}

