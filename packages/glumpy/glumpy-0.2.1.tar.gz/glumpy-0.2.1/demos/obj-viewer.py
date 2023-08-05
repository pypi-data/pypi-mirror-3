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

def load_obj(filename):
    '''
    Load vertices and faces from a wavefront .obj file and generate normals.
    '''
    data = np.genfromtxt(filename, dtype=[('type', np.character, 1),
                                          ('points', np.float32, 3)])

    # Get vertices and faces
    vertices = data['points'][data['type'] == 'v']
    faces = (data['points'][data['type'] == 'f']-1).astype(np.uint32)

    # Build normals
    T = vertices[faces]
    N = np.cross(T[::,1 ]-T[::,0], T[::,2]-T[::,0])
    L = np.sqrt(N[:,0]**2+N[:,1]**2+N[:,2]**2)
    N /= L[:, np.newaxis]
    normals = np.zeros(vertices.shape)
    normals[faces[:,0]] += N
    normals[faces[:,1]] += N
    normals[faces[:,2]] += N
    L = np.sqrt(normals[:,0]**2+normals[:,1]**2+normals[:,2]**2)
    normals /= L[:, np.newaxis]

    # Scale vertices such that object is contained in [-1:+1,-1:+1,-1:+1]
    vmin, vmax =  vertices.min(), vertices.max()
    vertices = 2*(vertices-vmin)/(vmax-vmin) - 1

    return vertices, normals, faces



if __name__ == '__main__':
    import sys


    if len(sys.argv) < 2:
         print 'Usage: obj-viewer.py objfile'
         sys.exit()
    vertices, normals, faces = load_obj(sys.argv[1])
    V = np.zeros(len(vertices), [('position', np.float32, 3),
                                 ('color', np.float32, 3),
                                 ('normal',   np.float32, 3)])
    V['position'] = vertices
    V['color'] = (vertices+1)/2.0
    V['normal'] = normals

    fig = gp.figure((300,300))
    frame = fig.add_frame()
    mesh = gp.graphics.VertexBuffer( V, faces )
    trackball = gp.Trackball( 65, 135, 1.0, 2.5 )

    @fig.event
    def on_init():
       gl.glLightfv (gl.GL_LIGHT0, gl.GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
       gl.glLightfv (gl.GL_LIGHT0, gl.GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
       gl.glLightfv (gl.GL_LIGHT0, gl.GL_SPECULAR,(0.0, 0.0, 0.0, 0.0))
       gl.glLightfv (gl.GL_LIGHT0, gl.GL_POSITION,(2.0, 2.0, 2.0, 0.0))
       gl.glEnable (gl.GL_LIGHTING)
       gl.glEnable (gl.GL_LIGHT0)

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
        gl.glEnable( gl.GL_POLYGON_OFFSET_FILL )
        gl.glPolygonOffset (1, 1)
        gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_FILL )
        mesh.draw( gl.GL_TRIANGLES, "pnc" )
        gl.glDisable( gl.GL_POLYGON_OFFSET_FILL )
        gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_LINE )
        gl.glEnable( gl.GL_BLEND )
        gl.glEnable( gl.GL_LINE_SMOOTH )
        gl.glColor( 0.0, 0.0, 0.0, 0.5 )
        mesh.draw( gl.GL_TRIANGLES, "p" )
        gl.glDisable( gl.GL_BLEND )
        gl.glDisable( gl.GL_LINE_SMOOTH )
        trackball.pop()
        frame.unlock()

    gp.show()

