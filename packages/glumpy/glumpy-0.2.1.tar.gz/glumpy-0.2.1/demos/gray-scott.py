#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright INRIA
# Contributors: Nicolas P. Rougier (Nicolas.Rougier@inria.fr)
#
# DANA is a computing framework for the simulation of distributed,
# asynchronous, numerical and adaptive models.
#
# This software is governed by the CeCILL license under French law and abiding
# by the rules of distribution of free software. You can use, modify and/ or
# redistribute the software under the terms of the CeCILL license as circulated
# by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info/index.en.html.
#
# As a counterpart to the access to the source code and rights to copy, modify
# and redistribute granted by the license, users are provided only with a
# limited warranty and the software's author, the holder of the economic
# rights, and the successive licensors have only limited liability.
#
# In this respect, the user's attention is drawn to the risks associated with
# loading, using, modifying and/or developing or reproducing the software by
# the user in light of its specific status of free software, that may mean that
# it is complicated to manipulate, and that also therefore means that it is
# reserved for developers and experienced professionals having in-depth
# computer knowledge. Users are therefore encouraged to load and test the
# software's suitability as regards their requirements in conditions enabling
# the security of their systems and/or data to be ensured and, more generally,
# to use and operate it in the same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
# -----------------------------------------------------------------------------
'''
Reaction Diffusion : Gray-Scott model

References:
----------
Complex Patterns in a Simple System
John E. Pearson, Science 261, 5118, 189-192, 1993.
'''
import numpy as np
import scipy.sparse as sp
import glumpy



def convolution_matrix(src, dst, kernel, toric=True):
    '''
    Build a sparse convolution matrix M such that:

    (M*src.ravel()).reshape(src.shape) = convolve2d(src,kernel)

    You can specify whether convolution is toric or not and specify a different
    output shape. If output (dst) is different, convolution is only applied at
    corresponding normalized location within the src array.

    Building the matrix can be pretty long if your kernel is big but it can
    nonetheless saves you some time if you need to apply several convolution
    compared to fft convolution (no need to go to the Fourier domain).

    Parameters:
    -----------

    src : n-dimensional numpy array
        Source shape

    dst : n-dimensional numpy array
        Destination shape

    kernel : n-dimensional numpy array
        Kernel to be used for convolution

    Returns:
    --------

    A sparse convolution matrix

    Examples:
    ---------

    >>> Z = np.ones((3,3))
    >>> M = convolution_matrix(Z,Z,Z,True)
    >>> print (M*Z.ravel()).reshape(Z.shape)
    [[ 9.  9.  9.]
     [ 9.  9.  9.]
     [ 9.  9.  9.]]
    >>> M = convolution_matrix(Z,Z,Z,False)
    >>> print (M*Z.ravel()).reshape(Z.shape)
    [[ 4.  6.  4.]
     [ 6.  9.  6.]
     [ 4.  6.  4.]]
    '''

    # Get non NaN value from kernel and their indices.
    nz = (1 - np.isnan(kernel)).nonzero()
    data = kernel[nz].ravel()
    indices = [0,]*(len(kernel.shape)+1)
    indices[0] = np.array(nz)
    indices[0] += np.atleast_2d((np.array(src.shape)//2 - np.array(kernel.shape)//2)).T

    # Generate an array A for a given shape such that given an index tuple I,
    # we can translate into a flat index F = (I*A).sum()
    to_flat_index = np.ones((len(src.shape),1), dtype=int)
    if len(src.shape) > 1:
        to_flat_index[:-1] = src.shape[1]

    R, C, D = [], [], []
    dst_index = 0
    src_indices = []

    # Translate target tuple indices into source tuple indices taking care of
    # possible scaling (this is done by normalizing indices)
    for i in range(len(src.shape)):
        z = np.rint((np.linspace(0,1,dst.shape[i])*(src.shape[i]-1))).astype(int)
        src_indices.append(z)

    nd = [0,]*(len(kernel.shape))
    for index in np.ndindex(dst.shape):
        dims = []
        # Are we starting a new dimension ?
        if index[-1] == 0:
            for i in range(len(index)-1,0,-1):
                if index[i]: break
                dims.insert(0,i-1)
        dims.append(len(dst.shape)-1)
        for dim in dims:
            i = index[dim]

            if toric:
                z = (indices[dim][dim] - src.shape[dim]//2 +(kernel.shape[dim]+1)%2 + src_indices[dim][i]) % src.shape[dim]
            else:
                z = (indices[dim][dim] - src.shape[dim]//2 +(kernel.shape[dim]+1)%2 + src_indices[dim][i])
            n = np.where((z >= 0)*(z < src.shape[dim]))[0]
            if dim == 0:
                nd[dim] = n.copy()
            else:
                nd[dim] = nd[dim-1][n]
            indices[dim+1] = np.take(indices[dim], n, 1)
            indices[dim+1][dim] = z[n]
        dim = len(dst.shape)-1
        z = indices[dim+1]
        R.extend( [dst_index,]*len(z[0]) )
        C.extend( (z*to_flat_index).sum(0).tolist() )
        D.extend( data[nd[-1]].tolist() )
        dst_index += 1

    return sp.coo_matrix( (D,(R,C)), (dst.size,src.size)).tocsr()


# Parameters from http://www.aliensaint.com/uo/java/rd/
# -----------------------------------------------------
n  = 150
dt = 1
t  = 10000
Du, Dv, F, k = 0.16, 0.08, 0.035, 0.065 # Bacteria 1
# Du, Dv, F, k = 0.14, 0.06, 0.035, 0.065 # Bacteria 2
# Du, Dv, F, k = 0.16, 0.08, 0.060, 0.062 # Coral
# Du, Dv, F, k = 0.19, 0.05, 0.060, 0.062 # Fingerprint
# Du, Dv, F, k = 0.10, 0.10, 0.018, 0.050 # Spirals
# Du, Dv, F, k = 0.12, 0.08, 0.020, 0.050 # Spirals Dense
# Du, Dv, F, k = 0.10, 0.16, 0.020, 0.050 # Spirals Fast
# Du, Dv, F, k = 0.16, 0.08, 0.020, 0.055 # Unstable
# Du, Dv, F, k = 0.16, 0.08, 0.050, 0.065 # Worms 1
# Du, Dv, F, k = 0.16, 0.08, 0.054, 0.063 # Worms 2
# Du, Dv, F, k = 0.16, 0.08, 0.035, 0.060 # Zebrafish

u = np.zeros((n,n), dtype = np.float32)
v = np.zeros((n,n), dtype = np.float32)
U = np.zeros((n,n), dtype = np.float32)
V = np.zeros((n,n), dtype = np.float32)
Z = U*V*V
K = convolution_matrix(Z,Z, np.array([[np.NaN,  1., np.NaN], 
                                      [  1.,   -4.,   1.  ],
                                      [np.NaN,  1., np.NaN]]))
Lu = (K*U.ravel()).reshape(U.shape)
Lv = (K*V.ravel()).reshape(V.shape)

r = 20
u[...] = 1.0
v[...] = 0.0
u[n/2-r:n/2+r,n/2-r:n/2+r] = 0.50
v[n/2-r:n/2+r,n/2-r:n/2+r] = 0.25
u += 0.05*np.random.random((n,n))
v += 0.05*np.random.random((n,n))
U[...] = u
V[...] = v

fig = glumpy.figure((512,512))
cmap = glumpy.colormap.Colormap("blue",
                                (0.00, (0.2, 0.2, 1.0)),
                                (1.00, (1.0, 1.0, 1.0)))
I = glumpy.Image(u, interpolation='bicubic', colormap=cmap)


@fig.event
def on_mouse_drag(x, y, dx, dy, button):
    global u,v,U,V,Z,Du,Dv,F,k,n
    center =( int((1-y/float(fig.width)) * (n-1)),
              int(   x/float(fig.height) * (n-1)) )
    def distance(x,y):
        return np.sqrt((x-center[0])**2+(y-center[1])**2)
    D = np.fromfunction(distance,(n,n))
    M = np.where(D<=5,True,False).astype(np.float32)
    U[...] = u[...] = (1-M)*u + M*0.50
    V[...] = v[...] = (1-M)*v + M*0.25
    I.update()


@fig.event
def on_draw():
    fig.clear()
    I.draw( x=0, y=0, z=0,
            width=fig.width, height=fig.height )

@fig.event
def on_idle(elapsed):
    global u,v,U,V,Z,Du,Dv,F,k
    for i in range(10):
        Lu = (K*U.ravel()).reshape(U.shape)
        Lv = (K*V.ravel()).reshape(V.shape)
        u += dt * (Du*Lu - Z +  F   *(1-U))
        v += dt * (Dv*Lv + Z - (F+k)*V    )
    #U,V = np.maximum(u,0), np.maximum(v,0)
        U,V = u, v
        Z = U*V*V
    I.update()
    fig.redraw()

glumpy.show()
