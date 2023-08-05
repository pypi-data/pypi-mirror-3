/* exoskelegram: An X11 key press/release catcher/sender wrapper
 * Copyright (C) 2011 Niels Serup
 *
 * This program is heavily based on xmacrorec (http://xmacro.sourceforge.net/),
 * released under the GPLv2+, portions Copyright (C) 2000 Gabor Keresztfalvi
 * <keresztg@mail.com> --- and xmacrorec is heavily based on xremote
 * (http://infa.abo.fi/~chakie/xremote/) which is copyright (C) 2000 Jan Ekholm
 * <chakie@infa.abo.fi>

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
 * Abstract filename: exoskelegram.xkeylib.xmacrorec.c
 */

#include "xmacrorec.h"

unsigned char xmacro_event_loop(Display *LocalDpy, int LocalScreen,
                                bool (*callback)(int, int, bool)) {
    int       status, index;
    KeyCode   keycode;
    KeySym    keysym;
    XEvent    event;
    XKeyEvent kevent;
    Window    root;
    bool      pressed, shift_on = false, mode_switch_on = false, loop = true;
  
    // get the root window and set default target
    root = RootWindow(LocalDpy, LocalScreen);
  
    // grab the keyboard
    status = XGrabKeyboard (LocalDpy, root, False, GrabModeSync, GrabModeAsync, CurrentTime);
  
    // did we succeed in grabbing the keyboard?
    if (status != GrabSuccess)
        // nope, abort
        return 2;

    status = 0;
    while (loop) {
        // allow one more event
        XAllowEvents(LocalDpy, SyncPointer, CurrentTime);	

        // get an event matching the specified mask
        XWindowEvent(LocalDpy, root, KeyPressMask|KeyReleaseMask, &event);

        if (event.type == KeyPress || event.type == KeyRelease) {
            // what did we get?
            pressed = (event.type == KeyPress ? true : false);
            kevent = event.xkey;
            keycode = kevent.keycode;
            keysym = XKeycodeToKeysym(LocalDpy, keycode, 0);
            if (keysym == XK_Shift_L || keysym == XK_Shift_R) {
                if (pressed)
                    shift_on = true;
                else
                    shift_on = false;
            }
            else if (keysym == XK_Mode_switch) {
                if (pressed)
                    mode_switch_on = true;
                else
                    mode_switch_on = false;
            }
            if (shift_on && mode_switch_on)
                index = 3;
            else if (mode_switch_on)
                index = 2;
            else if (shift_on)
                index = 1;
            else
                index = 0;
            keysym = XKeycodeToKeysym(LocalDpy, keycode, index);

            if ((*callback)(keycode, keysym, pressed))
                // stop
                loop = false;
        }
    }

    // we're done keyboard
    XUngrabKeyboard(LocalDpy, CurrentTime);
    return 0;
}

unsigned char xmacro_get_key_events(bool (*callback)(int, int, bool)) {
    unsigned char ret;

    // open the local display
    Display *LocalDpy = common_local_display;

    // get the screens too
    int LocalScreen = DefaultScreen(LocalDpy);

    // start the main event loop
    ret = xmacro_event_loop(LocalDpy, LocalScreen, callback);

    return ret;
}
