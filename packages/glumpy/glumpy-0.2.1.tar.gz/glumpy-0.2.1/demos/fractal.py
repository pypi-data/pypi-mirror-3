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
  
def mandel(n, m, itermax, xmin, xmax, ymin, ymax):  
    ''' 
    Fast mandelbrot computation using numpy. 
 
    (n, m) are the output image dimensions 
    itermax is the maximum number of iterations to do 
    xmin, xmax, ymin, ymax specify the region of the 
    set to compute. 

    code by: http://thesamovar.wordpress.com/
    '''  

    # The point of ix and iy is that they are 2D arrays giving the x-coord and
    # y-coord at each point in the array. The reason for doing this will become
    # clear below...

    ix, iy = numpy.mgrid[0:n, 0:m]  

    # Now x and y are the x-values and y-values at each point in the array,
    # linspace(start, end, n) is an array of n linearly spaced points between
    # start and end, and we then index this array using numpy fancy
    # indexing. If A is an array and I is an array of indices, then A[I] has
    # the same shape as I and at each place i in I has the value A[i].

    x = numpy.linspace(xmin, xmax, n)[ix]  
    y = numpy.linspace(ymin, ymax, m)[iy]  
    # c is the complex number with the given x, y coords  
    c = x+complex(0,1)*y  
    del x, y # save a bit of memory, we only need z  

    # the output image coloured according to the number of iterations it takes
    # to get to the boundary abs(z)>2

    img = numpy.zeros(c.shape, dtype=numpy.uint8)  

    # Here is where the improvement over the standard algorithm for drawing
    # fractals in numpy comes in.  We flatten all the arrays ix, iy and c. This
    # flattening doesn't use any more memory because we are just changing the
    # shape of the array, the data in memory stays the same. It also affects
    # each array in the same way, so that index i in array c has x, y coords
    # ix[i], iy[i]. The way the algorithm works is that whenever abs(z)>2 we
    # remove the corresponding index from each of the arrays ix, iy and
    # c. Since we do the same thing to each array, the correspondence between c
    # and the x, y coords stored in ix and iy is kept.

    ix.shape = n*m  
    iy.shape = n*m  
    c.shape = n*m  

    # we iterate z->z^2+c with z starting at 0, but the first iteration makes
    # z=c so we just start there.  We need to copy c because otherwise the
    # operation z->z^2 will send c->c^2.

    z = numpy.copy(c)  
    for i in xrange(itermax):  
        # all points have escaped equivalent to z = z*z+c but quicker and uses
        # less memory
        if not len(z):
            break
        numpy.multiply(z, z, z)  
        numpy.add(z, c, z)  
        # these are the points that have escaped  
        rem = numpy.abs(z)>2.0  
        # colour them with the iteration number, we add one so that points
        # which haven't escaped have 0 as their iteration number, this is why
        # we keep the arrays ix and iy because we need to know which point in
        # img to colour
        img[ix[rem], iy[rem]] = i+1  
        # -rem is the array of points which haven't  
        # escaped, in numpy -A for a boolean array A  
        # is the NOT operation.  
        rem = -rem  
        # So we select out the points in  
        # z, ix, iy and c which are still to be  
        # iterated on in the next step  
        z = z[rem]  
        ix, iy = ix[rem], iy[rem]  
        c = c[rem]  
    return img  



fig = glumpy.figure(size=(800,400))
fig1, fig2 = fig.split('horizontal')
frame1, frame2 = fig1.add_frame(aspect=1), fig2.add_frame(aspect=1)

n = 256
print 'Computing Mandelbrot set for size 2048x2028... '
Z = mandel(2048, 2048, 100, -2, .5, -1.25, 1.25) 
Z[Z==0] = 101
Z = Z.T
Z_scaled = numpy.log(Z[::4,::4]).astype(numpy.float32)
Z_zoomed = numpy.log(Z[:n,:n]).astype(numpy.float32)
I_scaled = glumpy.Image(Z_scaled, interpolation='bicubic', colormap=glumpy.colormap.Hot)
I_zoomed = glumpy.Image(Z_zoomed, interpolation='bicubic', colormap=glumpy.colormap.Hot)

@fig.event
def on_draw():
    fig.clear(0.85,0.85,0.85,1.00)

    frame1.draw(x=frame1.x, y=frame1.y)
    I_scaled.draw(x=frame1.x, y=frame1.y, z=0,
                  width=frame1.width,  height=frame1.height)

    frame2.draw(x=frame2.x, y=frame2.y)
    I_zoomed.draw(x=frame2.x, y=frame2.y, z=0,
                  width=frame2.width,  height=frame2.height)

@frame1.event
def on_mouse_motion(x,y,dx,dy):
    x = (      x/frame1.width ) * Z.shape[1] - n//2
    y = (1.0 - y/frame1.height) * Z.shape[0] - n//2
    x = int(min(max(x,0), Z.shape[1]-n))
    y = int(min(max(y,0), Z.shape[0]-n))
    Z_zoomed[...] = numpy.log(Z[y:y+n,x:x+n])
    I_zoomed.update()
    fig.redraw()
    
fig.show()

