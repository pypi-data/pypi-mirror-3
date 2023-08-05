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

# Create figure and frame
fig = glumpy.figure( size=(400,290) )
frame = fig.add_frame( size=(0.95,0.95) )

# Load image
Z = numpy.asarray( Image.open('stinkbug.png'))

# Split frame: one for image, one for colorbar
fig1,fig2 = frame.split( 'horizontal', size=0.05, spacing=0.01)
frame1 = fig1.add_frame( aspect = Z.shape[1]/float(Z.shape[0]), size = (1,1) )
frame2 = fig2.add_frame( size=(1,1) )

# Create a glumpy image out of Z
image = glumpy.image.Image(Z, colormap=glumpy.colormap.Hot)

# Create a colorbar array...
C = numpy.linspace(0,1,256).astype(numpy.float32).reshape((256,1,1))
# ... and make an image out of it
colorbar = glumpy.image.Image(C, colormap=glumpy.colormap.Hot)


@fig.event
def on_draw( ):
    fig.clear(1,1,1,0)
    x,y,z,w,h = frame1.x, frame1.y, 0, frame1.width, frame1.height
    frame1.draw( x, y )
    image.draw( x, y, z, w, h )    
    x,y,z,w,h = frame2.x,frame1.y,1, frame2.width, frame1.height
    frame2.draw( x,y,z, w, h )
    colorbar.draw( x, y, z, w, h)

fig.show()

