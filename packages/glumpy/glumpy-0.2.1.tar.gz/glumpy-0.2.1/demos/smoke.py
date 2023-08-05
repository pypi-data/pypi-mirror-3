#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# glumpy is an OpenGL framework for the fast visualization of numpy arrays.
# Copyright (C) 2009-2011  Nicolas P. Rougier. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY NICOLAS P. ROUGIER ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL NICOLAS P. ROUGIER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nicolas P. Rougier.
# -----------------------------------------------------------------------------
# Adapted from a post on comp.lang.python by Alberto Santini 
# Topic: Real-Time Fluid Dynamics for Games...
# Date: 02/20/05
# 
# Mouse click to add smoke
# Mouse move to add some turbulences
# -----------------------------------------------------------------------------
import sys
import numpy, glumpy
from solver import vel_step, dens_step

N = 50
size = N+2
dt = 0.1
diff = 0.0
visc = 0.0
force = 1
source = 25.0
u     = numpy.zeros((size,size), dtype=numpy.float32)
u_    = numpy.zeros((size,size), dtype=numpy.float32)
v     = numpy.zeros((size,size), dtype=numpy.float32)
v_    = numpy.zeros((size,size), dtype=numpy.float32)
dens  = numpy.zeros((size,size), dtype=numpy.float32)
dens_ = numpy.zeros((size,size), dtype=numpy.float32)
Z = numpy.zeros((N,N),dtype=numpy.float32)


fig = glumpy.figure((800,800))
fig.last_drag = None

cmap = glumpy.colormap.Colormap("BlueGrey",
                                (0., (0.,0.,0.)), (1., (0.75,0.75,1.00)))
I = glumpy.image.Image(Z, interpolation='bicubic',
                       colormap=cmap, vmin=0, vmax=5)
t, t0, frames = 0,0,0


@fig.event
def on_mouse_drag(x, y, dx, dy, button):
    fig.last_drag = x,y,dx,dy,button

@fig.event
def on_mouse_motion(x, y, dx, dy):
    fig.last_drag = x,y,dx,dy,0

@fig.event
def on_key_press(key, modifiers):
    global dens, dens_, u, u_, v, v_
    if key == glumpy.window.key.ESCAPE:
        sys.exit();
    elif key == glumpy.window.key.SPACE:
        dens[...] = dens_[...] = 0.0
        u[...] = u_[...] = 0.0
        v[...] = v_[...] = 0.0

@fig.event
def on_draw():
    fig.clear(0,0,0,1)
    I.draw(x=0, y=0, z=0,
           width=fig.width, height=fig.height)

@fig.event
def on_idle(*args):
    global dens, dens_, u, u_, v, v_, N, visc, dt, diff
    dens_[...] = u_[...] = v_[...] = 0.0
    if fig.last_drag:
        x,y,dx,dy,button = fig.last_drag
        j = min(max(int((N+2)*x/float(fig.width)),0),N+1)
        i = min(max(int((N+2)*(fig.height-y)/float(fig.height)),0),N+1)
        if not button:
            u_[i,j] = -force * dy
            v_[i,j] = force * dx
        else:
            dens_[i,j] = source
    fig.last_drag = None
    vel_step(N, u, v, u_, v_, visc, dt)
    dens_step(N, dens, dens_, u, v, diff, dt)
    Z[...] = dens[0:-2,0:-2]
    I.update()
    fig.redraw()

    global t, t0, frames
    t += args[0]
    frames = frames + 1
    if t-t0 > 5.0:
        fps = float(frames)/(t-t0)
        print 'FPS: %.2f (%d frames in %.2f seconds)' % (fps, frames, t-t0)
        frames,t0 = 0, t

glumpy.show()


