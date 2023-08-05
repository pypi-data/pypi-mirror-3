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
 * Abstract filename: exoskelegram.xkeylib.wrapper.c
 */

#include <Python.h>
#define XLIB_MODULE

#include "wrapper.h"
#include "xmacrorec.h"
#include "xmacrorec2.h"
#include "mapkey.h"
#include "sendkey.h"
#include "xmisc.h"

PyMODINIT_FUNC PyInit_xlib(void);
static PyObject* xlib_get_key_events(PyObject *self, PyObject *args);
static PyObject* xlib_map_key(PyObject *self, PyObject *args);
static PyObject* xlib_send_keycode(PyObject *self, PyObject *args);
static PyObject* xlib_keysym_to_keycode(PyObject *self, PyObject *args);
static PyObject* xlib_keycode_to_keysyms(PyObject *self, PyObject *args);
static PyObject* xlib_name_to_keysym(PyObject *self, PyObject *args);
static PyObject* xlib_xflush(PyObject *self, PyObject *args);

static PyObject *XlibError;
static PyObject *xlib_callback = NULL;


static PyMethodDef XlibMethods[] = {
    {"get_key_events", xlib_get_key_events, METH_VARARGS,
     "get_key_events(callback, lock=False)\n\n"
     "Get X key events and send them to a callback function\n"
     "func(keycode:int, keysym:int, pressed|released:bool). \n"
     "If func returns True, stop. If lock, make X server unresponsive "
     "to all key input.\n"
     "WARNING: If lock is True and your callback function never returns True,\n"
     "it will not be easy to regain control of your X server."},
    {"map_key", xlib_map_key, METH_VARARGS,
     "map_key(keycode_from, [keysyms])\n\n"
     "Map a key to another key."},
    {"xflush", xlib_xflush, METH_VARARGS,
     "xflush()\n\nFlush X."},
    {"send_keycode", xlib_send_keycode, METH_VARARGS,
     "send_keycode(keycode, pressed=True)\n\n"
     "Send a key by its keycode."},
    {"keysym_to_keycode", xlib_keysym_to_keycode, METH_VARARGS,
     "keysym_to_keycode(keysym) -> keycode\n\n"
     "Convert a keysym to its matching keycode and return it if it exists,\n"
     "else return 0."},
    {"keycode_to_keysyms", xlib_keycode_to_keysyms, METH_VARARGS,
     "keycode_to_keysyms(keycode) -> [keysyms]\n\n"
     "Convert a keycode to its four keysyms (no modifiers, with Shift,\n"
     "with Mode_Switch, with Shift+Mode_Switch"},
    {"name_to_keysym", xlib_name_to_keysym, METH_VARARGS,
     "name_to_keysym(name) -> keysym\n\n"
     "Convert an XString to its matching keysym and return it."},
    {NULL, NULL, 0, NULL} // Sentinel
};

static struct PyModuleDef xlibmodule = {
   PyModuleDef_HEAD_INIT,
   "_xlib",   /* name of module */
   NULL,     /* module documentation, may be NULL */
   -1,      /* size of per-interpreter state of the module,
               or -1 if the module keeps state in global variables. */
   XlibMethods
};

PyMODINIT_FUNC PyInit__xlib(void) {
    PyObject *m;

    m = PyModule_Create(&xlibmodule);
    if (m == NULL)
        return NULL;

    XlibError = PyErr_NewException("_xlib.error", NULL, NULL);
    Py_INCREF(XlibError);
    PyModule_AddObject(m, "error", XlibError);
    if (common_init() == true) {
        PyErr_SetString(XlibError, "Unable to open local X display");
        return NULL;
    }
    Py_AtExit(common_unload);
    return m;
}

static PyObject* xlib_get_key_events(PyObject *self, PyObject *args) {
    PyObject *temp_callback;
    PyObject *temp_lock = Py_False;
    bool lock;
    /* STRANGE: When this function has been called just once with temp_lock as
       Py_True, temp_lock will stay equal to Py_True in all subsequent calls,
       both when temp_lock is False and when it isn't given. MUSTFIX. */

    if (PyArg_ParseTuple(args, "O|O", &temp_callback, &temp_lock)) {
        if (!PyCallable_Check(temp_callback)) {
            PyErr_SetString(PyExc_TypeError, "callback must be callable");
            return NULL;
        }
        Py_XINCREF(temp_callback);
        Py_XINCREF(temp_lock);
        Py_XDECREF(xlib_callback);
        xlib_callback = temp_callback;
        lock = PyObject_IsTrue(temp_lock);
        if (lock) {
            switch (xmacro_get_key_events(call_xlib_callback)) {
            case 0:
                Py_INCREF(Py_None);
                return Py_None;

            case 1:
                PyErr_SetString(XlibError, "Unable to open display");
                return NULL;

            case 2:
                PyErr_SetString(XlibError, "Could not grab the local keyboard");
                return NULL;
            }
        }
        else {
            switch (xmacro2_get_key_events(call_xlib_callback)) {
            case 0:
                Py_INCREF(Py_None);
                return Py_None;

            case 1:
                PyErr_SetString(XlibError, "Unable to open display");
                return NULL;

            case 2:
                PyErr_SetString(XlibError, "XRecord extension not supported on X server");
                return NULL;

            case 3:
                PyErr_SetString(XlibError, "Could not allocate record range");
                return NULL;

            case 4:
                PyErr_SetString(XlibError, "Could not create a record context");
                return NULL;

            case 5:
                PyErr_SetString(XlibError, "Could not enable the record context");
                return NULL;
            }
        }
    }
    return NULL;
}

bool call_xlib_callback(int keycode, int keysym, bool pressed) {
    PyObject *arglist, *result, *pressed_pybool;
    pressed_pybool = (pressed ? Py_True : Py_False);
    Py_INCREF(pressed_pybool);
    arglist = Py_BuildValue("(i,i,O)", keycode, keysym, pressed_pybool);
    result = PyObject_CallObject(xlib_callback, arglist);
    Py_DECREF(arglist);
    return (PyObject_IsTrue(result) ? true : false);
}

static PyObject* xlib_xflush(PyObject *self, PyObject *args) {
    xmisc_xflush();
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* xlib_send_keycode(PyObject *self, PyObject *args) {
    KeyCode keycode;
    PyObject* pressed_pybool = Py_True;
    bool pressed;

    if (PyArg_ParseTuple(args, "i|O", &keycode, &pressed_pybool)) {
        Py_XINCREF(pressed_pybool);
        pressed = (PyObject_IsTrue(pressed_pybool) ? true : false);
        switch (sendkey_send_key(keycode, pressed)) {
        case 1:
            PyErr_SetString(XlibError, "XTEST extension not supported");
            return NULL;

        case 2:
            PyErr_SetString(XlibError, "Something went wrong");
            return NULL;

        default:
            Py_INCREF(Py_None);
            return Py_None;
        }
    }
    return NULL;
}

static PyObject* xlib_map_key(PyObject *self, PyObject *args) {
    int i;
    KeyCode keycode;
    KeySym k;
    KeysymList* ks;
    Py_ssize_t len;
    PyObject* py_keysyms;

    if (PyArg_ParseTuple(args, "iO", &keycode, &py_keysyms)) {
        Py_XINCREF(py_keysyms);
        len = PySequence_Length(py_keysyms);
        if (len < 1) {
            PyErr_SetString(XlibError, "Number of keysyms must be above 0");
            return NULL;
        }
        ks = (KeysymList*) malloc(sizeof(KeysymList));
        for (i = 0; i < len; i++) {
            k = (KeySym) PyNumber_AsSsize_t(PySequence_GetItem(py_keysyms, i),
                                            NULL);
            ks->keysyms[i] = k;
        }
        for (; i < 4; i++) {
            ks->keysyms[i] = k;
        }
        switch (mapkey_map_key(keycode, ks)) {
        case BadValue:
            PyErr_SetString(XlibError, "Numeric value out of range");
            return NULL;

        case BadAlloc:
            PyErr_SetString(XlibError, "Not enough memory");
            return NULL;

        default:
            Py_INCREF(Py_None);
            return Py_None;
        }
    }
    return NULL;
}

static PyObject* xlib_keysym_to_keycode(PyObject *self, PyObject *args) {
    KeySym keysym;
    PyObject* py_keycode;
    if (PyArg_ParseTuple(args, "i", &keysym)) {
        py_keycode = Py_BuildValue("i", xmisc_keysym_to_keycode(keysym));
        Py_INCREF(py_keycode);
        return py_keycode;
    }
    return NULL;
}

static PyObject* xlib_keycode_to_keysyms(PyObject *self, PyObject *args) {
    int i;
    KeyCode keycode;
    KeysymList* ks;
    PyObject* py_keysyms;
    if (PyArg_ParseTuple(args, "i", &keycode)) {
        ks = xmisc_keycode_to_keysyms(keycode);
        py_keysyms = PyList_New(4);
        Py_INCREF(py_keysyms);
        for (i = 0; i < 4; i++)
            PyList_SetItem(py_keysyms, i, Py_BuildValue("i", ks->keysyms[i]));
        return py_keysyms;
    }
    return NULL;
}

static PyObject* xlib_name_to_keysym(PyObject *self, PyObject *args) {
    char* name;
    PyObject* py_keysym;
    if (PyArg_ParseTuple(args, "s", &name)) {
        py_keysym = Py_BuildValue("i", xmisc_string_to_keysym(name));
        Py_INCREF(py_keysym);
        return py_keysym;
    }
    return NULL;
}
