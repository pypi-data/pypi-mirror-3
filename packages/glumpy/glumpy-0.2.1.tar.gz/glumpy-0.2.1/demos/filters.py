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


fig = glumpy.figure(size=(800,800))

frames = []
for i in range(4):
    for j in range(4):
        frame = fig.add_figure(cols=4,rows=4, position=[i,j]).add_frame(aspect=1)
        frames.append(frame)

def func3(x,y):
    return (1-x/2+x**5+y**3)*numpy.exp(-x**2-y**2)
x = numpy.linspace(-3.0, 3.0, 12)
y = numpy.linspace(-3.0, 3.0, 12)
Z = func3(*numpy.meshgrid(x, y)).astype(numpy.float32)

images = []
for interpolation in ['nearest', 'bilinear', 'hanning',  'hamming',
                      'hermite', 'kaiser',   'quadric',  'bicubic',
                      'catrom',  'spline16', 'spline16', 'spline36',
                      'gaussian', 'bessel',   'sinc',    'lanczos']:
    images.append( glumpy.image.Image(Z, interpolation=interpolation,
                                      colormap = glumpy.colormap.IceAndFire,
                                      grid_size=(0,0,0)) )

@fig.event
def on_draw():
    fig.clear(0.85,0.85,0.85,1.00)
    for frame in frames:
        frame.draw(x=frame.x, y=frame.y)
    for image,frame in zip(images,frames):
        image.draw(x=frame.x, y=frame.y, z= 0,
                   width=frame.width,  height=frame.height)

glumpy.show()
