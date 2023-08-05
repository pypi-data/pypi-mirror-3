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
import numpy, glumpy
from PIL import Image


fig   = glumpy.figure(size=(800,400))
frame = fig.add_figure(cols=8,rows=4,size=[4,4]).add_frame(aspect=1, size=[.975,.975])


I    = numpy.asarray( Image.open('lena.png'), dtype=numpy.uint8)
lena = glumpy.image.Image(I, interpolation=None)
n = 16
zoom = numpy.zeros((n,n,3), dtype=numpy.uint8)
zoom[...] = lena.data[0:n,0:n]


frames = []
for i in range(4):
    for j in range(4):
        frames.append(
            fig.add_figure(cols=8,rows=4, position=[4+i,j]).add_frame(aspect=1) )

images = []
for interpolation in ['nearest', 'bilinear', 'hanning',  'hamming',
                      'hermite', 'kaiser',   'quadric',  'bicubic',
                      'catrom',  'spline16', 'spline16', 'spline36',
                      'gaussian', 'bessel',   'sinc',    'lanczos']:
    images.append( glumpy.image.Image(zoom, interpolation=interpolation) )

@fig.event
def on_draw():
    fig.clear(0.85,0.85,0.85,1.00)
    frame.draw(x=frame.x, y=frame.y)
    lena.draw(x=frame.x, y=frame.y, z=0,
              width=frame.width,  height=frame.height)
    for i in range(len(frames)):
        frames[i].draw(x=frames[i].x, y=frames[i].y)
        images[i].draw(x=frames[i].x, y=frames[i].y, z=0,
                       width=frames[i].width,  height=frames[i].height)

@frame.event
def on_mouse_motion(x,y,dx,dy):
    x = (      x/frame.width ) * lena.width - n//2
    y = (1.0 - y/frame.height) * lena.height - n//2
    x = int(min(max(x,0), lena.width-n))
    y = int(min(max(y,0), lena.height-n))
    zoom[...] = lena.data[y:y+n, x:x+n]
    for i in range(len(images)):
        images[i].update()
    fig.redraw()
    
fig.show()

