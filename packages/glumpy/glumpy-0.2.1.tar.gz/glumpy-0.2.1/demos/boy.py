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
import numpy as np
import glumpy as gp
import OpenGL.GL as gl

# Generate Boy surface
#  (-> from mayavi boy example)
u,v = np.mgrid[-0.035:np.pi:0.01, -0.035:np.pi:0.01]
X = 2/3.* (np.cos(u)* np.cos(2*v)
        + np.sqrt(2)* np.sin(u)* np.cos(v))* np.cos(u) / (np.sqrt(2) - np.sin(2*u)* np.sin(3*v))
Y = 2/3.* (np.cos(u)* np.sin(2*v) - np.sqrt(2)* np.sin(u)* np.sin(v))* np.cos(u) / (np.sqrt(2)
        - np.sin(2*u)* np.sin(3*v))
Z = -np.sqrt(2)* np.cos(u)* np.cos(u) / (np.sqrt(2) - np.sin(2*u)* np.sin(3*v))

S = np.sin(u)
S = (S - S.min())/ (S.max()-S.min())
n = len(X)

# Make a mesh out of it
vertices = np.zeros( (n*n), dtype = [ ('position','f4', 3),
                                      ('color',   'f4', 3) ] )
vertices['position'][...,0] = X.ravel()
vertices['position'][...,1] = Y.ravel()
vertices['position'][...,2] = Z.ravel()
vertices['color'][...,0] = S.ravel()
vertices['color'][...,1] = S.ravel()
vertices['color'][...,2] = S.ravel()

# Rescale and center
V = vertices['position']
vmin, vmax =  V.min(), V.max()
V[...] = 3.0 * (V-vmin)/(vmax-vmin)
xmin, xmax = V[...,0].min(), V[...,0].max()
vertices['position'][...,0] -= (xmax+xmin)/2.0
ymin, ymax = V[...,1].min(), V[...,1].max()
vertices['position'][...,1] -= (ymax+ymin)/2.0
zmin, zmax = V[...,2].min(), V[...,2].max()
vertices['position'][...,2] -= (zmax+zmin)/2.0

# Make indices
indices = []
for i in range(n):
    for j in range(n):
        indices.extend( [((j+0)   )*n + i,
                         ((j+0)   )*n + (i+1)%n,
                         ((j+1)%n )*n + (i+1)%n,
                         ((j+1)%n )*n + i ])
indices = np.array(indices, dtype=np.uint32)


# Display mesh
fig = gp.figure((512,512))
frame = fig.add_frame()
mesh = gp.graphics.VertexBuffer( vertices , indices )
trackball = gp.Trackball( 0, 0, 1., 4.5 )

@fig.event
def on_mouse_drag(x,y,dx,dy,button):
    trackball.drag_to(x,y,dx,dy)
    fig.redraw()

@fig.event
def on_draw():
    fig.clear(0.85,0.85,0.85,1)

@frame.event
def on_draw():
    frame.lock()
    frame.draw()
    trackball.push()
    mesh.draw( gl.GL_QUADS )
    trackball.pop()
    frame.unlock()

gp.show()
