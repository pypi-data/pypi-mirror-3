#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import sys
import glumpy

fig = glumpy.figure()

@fig.event
def on_draw():
    fig.clear()

@fig.event
def on_key_press(symbol, modifiers):
    if symbol == glumpy.window.key.TAB:
        if fig.window.get_fullscreen():
            fig.window.set_fullscreen(0)
        else:
            fig.window.set_fullscreen(1)
    if symbol == glumpy.window.key.ESCAPE:
        sys.exit()

fig.show()
