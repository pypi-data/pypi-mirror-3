/* exoskelegram: An X11 key press/release catcher/sender wrapper
 * Copyright (C) 2011 Niels Serup
 *
 * This program is heavily based on xmacrorec2 (http://xmacro.sourceforge.net/),
 * released under the GPLv2+, portions Copyright (C) 2000 Gabor Keresztfalvi
 * <keresztg@mail.com> --- and xmacrorec2 is heavily based on xremote
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
 * Abstract filename: exoskelegram.xkeylib.xmacrorec2.c
 */

#include "xmacrorec2.h"

typedef struct {
    int status, doit;
    Display *LocalDpy, *RecDpy;
    XRecordContext rc;
    bool shift_on, mode_switch_on;
    bool (*callback)(int, int, bool);
} Priv;

static void xmacro2_event_callback(XPointer priv, XRecordInterceptData *d);

static unsigned char xmacro2_event_loop(Display *LocalDpy, int LocalScreen,
                                        Display *RecDpy,
                                        bool (*callback)(int, int, bool));

static void xmacro2_event_callback(XPointer priv, XRecordInterceptData *d) {
    Priv *p = (Priv *) priv;
    unsigned char *ud, type;
    KeyCode keycode;
    KeySym keysym;
    int index;
    bool pressed;

    if (d->category != XRecordFromServer || p->doit == 0)
        goto returning;

    ud = (unsigned char *) d->data;

    type    = ud[0] & 0x7F;
    keycode = ud[1];

    if (p->status) {
        p->status--;
        if (type == KeyRelease)
            goto returning;
        else
            p->status = 0;
    }

    if (type == KeyPress || type == KeyRelease) {
        pressed = (type == KeyPress ? true : false);
        // what did we get?
        keysym = XKeycodeToKeysym(p->LocalDpy, keycode, 0);
        if (keysym == XK_Shift_L || keysym == XK_Shift_R) {
            if (pressed)
                p->shift_on = true;
            else
                p->shift_on = false;
        }
        else if (keysym == XK_Mode_switch) {
            if (pressed)
                p->mode_switch_on = true;
            else
                p->mode_switch_on = false;
        }
        if (p->shift_on && p->mode_switch_on)
            index = 3;
        else if (p->mode_switch_on)
            index = 2;
        else if (p->shift_on)
            index = 1;
        else
            index = 0;
        keysym = XKeycodeToKeysym(p->LocalDpy, keycode, index);

        // KeyPress == true, KeyRelease == false
        if ((*p->callback)(keycode, keysym, pressed))
            // stop
            p->doit = 0;
    }

 returning:
    XRecordFreeData(d);
}


static unsigned char xmacro2_event_loop(Display *LocalDpy, int LocalScreen,
                                        Display *RecDpy,
                                        bool (*callback)(int, int, bool)) {
    XRecordContext rc;
    XRecordRange *rr;
    XRecordClientSpec rcs;
    Priv priv;
    Status sret;
    Window Root;
  
    // get the root window and set default target
    Root = RootWindow(LocalDpy, LocalScreen);

    rr = XRecordAllocRange();
    if (!rr)
        return 3;

    rr->device_events.first = KeyPress;
    rr->device_events.last = MotionNotify;
    rcs = XRecordAllClients;
    rc = XRecordCreateContext(RecDpy, 0, &rcs, 1, &rr, 1);
    if (!rc)
        return 4;

    priv.status = 2;
    priv.doit = 1;
    priv.LocalDpy = LocalDpy;
    priv.RecDpy = RecDpy;
    priv.rc = rc;
    priv.shift_on = false;
    priv.mode_switch_on = false;
    priv.callback = callback;

    if (!XRecordEnableContextAsync(RecDpy, rc, xmacro2_event_callback,
                                   (XPointer) &priv))
        return 5;

    while (priv.doit)
        XRecordProcessReplies(RecDpy);

    sret = XRecordDisableContext(LocalDpy, rc);
    XFree(rr);
    return 0;
}


unsigned char xmacro2_get_key_events(bool (*callback)(int, int, bool)) {
    int major, minor;
    unsigned char ret;
  
    // open the local display twice
    Display *LocalDpy = common_local_display;
    Display *RecDpy = common_get_local_display();
    if (RecDpy == NULL)
        return 1;

    // get the screens too
    int LocalScreen = DefaultScreen(LocalDpy);

    // does the remote display have the Xrecord-extension?
    if (!XRecordQueryVersion(RecDpy, &major, &minor)) {
        // nope, extension not supported
        // close the display and go away
        XCloseDisplay(RecDpy);
        return 2;
    }

    // start the main event loop
    ret = xmacro2_event_loop(LocalDpy, LocalScreen, RecDpy, callback);

    return ret;
}
