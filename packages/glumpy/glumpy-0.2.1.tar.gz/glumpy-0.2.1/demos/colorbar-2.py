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

Z = numpy.asarray( Image.open('stinkbug.png'))

fig = glumpy.figure( size=(400,290) )
frame = fig.add_frame( aspect = Z.shape[1]/float(Z.shape[0]),
                       size=(0.975,0.975) )
subfig = glumpy.Figure(size=(.5,.05), position=(.45,.90), parent=fig)
subframe = subfig.add_frame( size=(1,1), aspect = 10 )

image = glumpy.image.Image(Z, colormap=glumpy.colormap.Hot)

C = numpy.linspace(0,1,256).astype(numpy.float32)
C = C.reshape((1,256))
colorbar = glumpy.image.Image(C, colormap=glumpy.colormap.Hot)

@fig.event
def on_draw( ):
    fig.clear(1,1,1,0)
    frame.draw( x=frame.x, y=frame.y )
    image.draw( x=frame.x, y=frame.y,  z = 0,
                width=frame.width, height=frame.height )
    subframe.draw( x=frame.x+5, y=frame.y+5 )
    colorbar.draw( x=frame.x+5, y=frame.y+5, z = 1,
                   width=subframe.width, height=subframe.height )    

fig.show()

