#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import numpy  as np
import glumpy as gp

fig = gp.figure( (512,512) )

def func3(x,y):return (1-x/2+x**5+y**3)*np.exp(-x**2-y**2)
x = np.linspace(-3.0, 3.0, 64).astype(np.float32)
Z = func3(*np.meshgrid(x,x))

cmap = gp.colormap.Grey
cmap.set_under(0.,0.,1.,1.)
cmap.set_over(1.,0.,0.,1.)
image = gp.image.Image(Z, colormap = cmap, vmin= -0.5, vmax = 0.5)

@fig.event
def on_draw():
    fig.clear()
    image.draw( x=0, y=0, z=0, width=fig.width, height=fig.height )

gp.show()
