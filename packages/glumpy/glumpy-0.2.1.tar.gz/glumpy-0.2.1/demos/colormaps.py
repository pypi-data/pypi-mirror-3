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
'''
This example demomonstrates frame aspects.
'''
import numpy
import glumpy

fig = glumpy.figure(size=(640,480))
colormaps = [ glumpy.colormap.IceAndFire,
              glumpy.colormap.Ice,
              glumpy.colormap.Fire,
              glumpy.colormap.Hot,
              glumpy.colormap.Grey,
              glumpy.colormap.Grey_r,
              glumpy.colormap.DarkRed,
              glumpy.colormap.DarkGreen,
              glumpy.colormap.DarkBlue,
              glumpy.colormap.LightRed,
              glumpy.colormap.LightGreen,
              glumpy.colormap.LightBlue ]
n = len(colormaps)

frames = []
for i in range(n):
    figure = fig.add_figure(cols=1, rows=n, position=[0,i] )
    frame = figure.add_frame( size=(0.99,0.8) )
    frames.append(frame)
Z = numpy.linspace(0.0, 1.0, 256).astype(numpy.float32)
#Z = Z.reshape((1,256))

images = []
for i in range(n):
    images.append(
        glumpy.image.Image( Z, colormap = colormaps[i], vmin=0, vmax=1 ) )

@fig.event
def on_draw():
    fig.clear(0.85,0.85,0.85,1.00)
    for frame in frames:
        frame.draw(x=frame.x, y=frame.y)

    for image,frame in zip(images,frames):
        image.draw(x=frame.x, y=frame.y, z= 0,
                   width=frame.width,  height=frame.height)

glumpy.show()
