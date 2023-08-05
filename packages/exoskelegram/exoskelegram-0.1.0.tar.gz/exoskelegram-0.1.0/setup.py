#!/usr/bin/env python3
# Maintainer: Niels Serup <ns@metanohi.name>
# Abstract filename: exoskelegram.setup

import os.path
from distutils.core import setup, Extension

_dirname = os.path.abspath(os.path.dirname(__file__))
os.chdir(_dirname)

_c_module = Extension('exoskelegram.xkeylib._xlib',
                      sources=[os.path.join(_dirname, f) for f in (
            'exoskelegram/xkeylib/wrapper.c',
            'exoskelegram/xkeylib/common.c',
            'exoskelegram/xkeylib/xmacrorec.c',
            'exoskelegram/xkeylib/xmacrorec2.c',
            'exoskelegram/xkeylib/mapkey.c',
            'exoskelegram/xkeylib/sendkey.c',
            'exoskelegram/xkeylib/xmisc.c',
            )], libraries=['X11', 'Xtst'])

setup(
    name='exoskelegram',
    version='0.1.0',
    author='Niels Serup',
    author_email='ns@metanohi.name',
    packages=['exoskelegram', 'exoskelegram.xkeylib', 'exoskelegram.data'],
    package_data={'': ['data/keysyms.txt']},
    scripts=['scripts/exoskelegram'],
    url='http://metanohi.name/projects/exoskelegram/',
    license='AGPLv3+',
    description='An X11 key press/release catcher/sender wrapper with abstractions',
    long_description=open(os.path.join(_dirname, 'README.txt')).read(),
    ext_modules = [_c_module],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'Environment :: Console',
                 'Environment :: X11 Applications',
                 'Topic :: Utilities',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Other/Nonlisted Topic',
                 'License :: DFSG approved',
                 'License :: OSI Approved :: GNU Affero General Public License v3',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.1',
                 'Programming Language :: C',
                 ])

