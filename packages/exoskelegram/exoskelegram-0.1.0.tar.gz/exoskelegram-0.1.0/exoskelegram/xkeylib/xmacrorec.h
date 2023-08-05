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
 * Abstract filename: exoskelegram.xkeylib.xmacrorec.h
 */

#ifndef EXOSKELEGRAM_XMACRORECHEADER
#define EXOSKELEGRAM_XMACRORECHEADER

#include "common.h"

unsigned char xmacro_get_key_events(bool (*callback)(int, int, bool));

unsigned char xmacro_event_loop(Display *LocalDpy, int LocalScreen,
                                bool (*callback)(int, int, bool));

Display* xmacro_get_remote_display(const char *DisplayName);

#endif
