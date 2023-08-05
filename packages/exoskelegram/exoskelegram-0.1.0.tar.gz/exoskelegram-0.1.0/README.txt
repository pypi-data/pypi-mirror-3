
============
exoskelegram
============

exoskelegram is an X11 key press/release catcher/sender wrapper with
abstractions. In a future release, in addition to being able to catch
and send X key events from Python programs, exoskelegram will allow
you to use simple config files to temporarily reprogram your entire
keyboard --- or just a part of it.

License
=======

exoskelegram is free software under the terms of the GNU Affero General Public
License version 3 (or any later version). This is version 0.1.0 of the program.

Contact
=======

The author of exoskelegram is Niels Serup. Bug reports and suggestions should
be sent to ns@metanohi.name for the time being.


Installation
============

Dependencies
------------

exoskelegram requires the X11 headers and the Xtst extension. If you're using a
package manager, remember to install the development packages (``*-dev`` or
``*-devel`` or something similar).

Way #1
------
Get the newest version of exoskelegram at
http://metanohi.name/projects/exoskelegram/ or at
http://pypi.python.org/pypi/exoskelegram

Extract exoskelegram from the downloaded file, cd into it and run this in a
terminal::

  # python3 setup.py install

Examples are available in the ``examples`` directory.

Way #2
------
Just run this::

  # pip-3.1 install exoskelegram

Note that this will not make any examples available.


Use
===

As a command-line tool
----------------------

Run ``exoskelegram`` to use it. Run ``exoskelegram --help`` to see how to use it.

As a module
-----------

To find out how to use it, run::

  $ pydoc3 exoskelegram.xkeylib


Examples
--------

There are a few examples in the ``examples`` directory. None of them apply to
the current few-features version.


Development
===========

exoskelegram uses Git for code management. The newest (and perhaps unstable)
code is available at::

  $ git clone git://gitorious.org/exoskelegram/exoskelegram.git


This document
=============

Copyright (C) 2011 Niels Serup

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and this
notice are preserved.  This file is offered as-is, without any warranty.
