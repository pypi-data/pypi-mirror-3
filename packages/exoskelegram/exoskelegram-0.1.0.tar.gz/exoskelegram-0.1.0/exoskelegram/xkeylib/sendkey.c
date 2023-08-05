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
 * Abstract filename: exoskelegram.xkeylib.sendkey.c
 */

#include "sendkey.h"

unsigned char sendkey_send_key(int keycode, bool pressed) {
    int major, minor, event_base, error_base;
    if (!XTestQueryExtension(common_local_display, &event_base,
                             &error_base, &major, &minor)) {
        // nope, extension not supported
        return 1;
    }
    if (XTestFakeKeyEvent(common_local_display, keycode, pressed, 0) != 0)
        return 0;
    else
        return 2;
}
