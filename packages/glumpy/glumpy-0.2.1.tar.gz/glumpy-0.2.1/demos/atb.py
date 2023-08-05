#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2008, dunkfordyce - 2010, Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import sys
import numpy
import glumpy
import glumpy.atb as atb
import OpenGL.GL as gl
from ctypes import *



def quit(*args, **kwargs):
    sys.exit()

if __name__ == '__main__':
    
    fig = glumpy.figure((640,480))
    trackball = glumpy.Trackball(45,135,1.25,3.5)
    atb.init()


    s = 0.5
    p = ( ( s, s, s), (-s, s, s), (-s,-s, s), ( s,-s, s),
          ( s,-s,-s), ( s, s,-s), (-s, s,-s), (-s,-s,-s) )
    n = ( ( 0, 0, 1), (1, 0, 0), ( 0, 1, 0),
          (-1, 0, 1), (0,-1, 0), ( 0, 0,-1) );
    c = ( ( 1, 1, 1), ( 1, 1, 0), ( 1, 0, 1), ( 0, 1, 1),
          ( 1, 0, 0), ( 0, 0, 1), ( 0, 1, 0), ( 0, 0, 0) );
    vertices = numpy.array(
        [ (p[0],n[0],c[0]), (p[1],n[0],c[1]), (p[2],n[0],c[2]), (p[3],n[0],c[3]),
          (p[0],n[1],c[0]), (p[3],n[1],c[3]), (p[4],n[1],c[4]), (p[5],n[1],c[5]),
          (p[0],n[2],c[0]), (p[5],n[2],c[5]), (p[6],n[2],c[6]), (p[1],n[2],c[1]),
          (p[1],n[3],c[1]), (p[6],n[3],c[6]), (p[7],n[3],c[7]), (p[2],n[3],c[2]),
          (p[7],n[4],c[7]), (p[4],n[4],c[4]), (p[3],n[4],c[3]), (p[2],n[4],c[2]),
          (p[4],n[5],c[4]), (p[7],n[5],c[7]), (p[6],n[5],c[6]), (p[5],n[5],c[5]) ], 
        dtype = [('position','f4',3), ('normal','f4',3), ('color','f4',3)] )
    cube = glumpy.graphics.VertexBuffer(vertices)
    cube.size = [0.5,0.5,0.5]

    bar = atb.Bar(name="Controls", label="Controls",
                  help="Scene controls", position=(10, 10), size=(200, 320))

    fill = c_bool(1)
    color = (c_float * 3)(1.0,1.0,0.3)
    shape = c_int()
    bar.add_var("Trackball/Phi", step=0.5,
                getter=trackball._get_phi, setter=trackball._set_phi)
    bar.add_var("Trackball/Theta", step=0.5,
                getter=trackball._get_theta, setter=trackball._set_theta)
    bar.add_var("Trackball/Zoom", step=0.01,
                getter=trackball._get_zoom, setter=trackball._set_zoom)
    bar.add_var("Object/Fill", fill)
    bar.add_var("Object/Color", color, open=True)

    def get_size_x():
        return cube.size[0]
    def set_size_x(value):
        scale = float(value)/cube.size[0]
        cube.size[0] = value
        cube.vertices['position'][:,0] *= scale
        cube.upload()

    def get_size_y():
        return cube.size[1]
    def set_size_y(value):
        scale = float(value)/cube.size[1]
        cube.size[1] = value
        cube.vertices['position'][:,1] *= scale
        cube.upload()

    def get_size_z():
        return cube.size[2]
    def set_size_z(value):
        scale = float(value)/cube.size[2]
        cube.size[2] = value
        cube.vertices['position'][:,2] *= scale
        cube.upload()

    bar.add_var("Object/Size/X", step=0.01,
                getter=get_size_x, setter=set_size_x)
    bar.add_var("Object/Size/Y", step=0.01,
                getter=get_size_y, setter=set_size_y)
    bar.add_var("Object/Size/Z", step=0.01,
                getter=get_size_z, setter=set_size_z)
    bar.add_separator("")
    bar.add_button("Quit", quit, key="ESCAPE", help="Quit application")


    def draw_background():
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        gl.glDisable (gl.GL_LIGHTING)
        gl.glDisable (gl.GL_DEPTH_TEST);
        gl.glBegin(gl.GL_QUADS)
        gl.glColor(1.0,1.0,1.0)
        gl.glVertex(0,0,-1)
        gl.glVertex(viewport[2],0,-1)
        gl.glColor(0.0,0.0,1.0)
        gl.glVertex(viewport[2],viewport[3],0)
        gl.glVertex(0,viewport[3],0)
        gl.glEnd()

    def draw_scene():
        if fill.value:
            gl.glEnable (gl.GL_LIGHTING)
            gl.glEnable (gl.GL_DEPTH_TEST)
            gl.glColor3f(color[0],color[1],color[2])
            gl.glPolygonOffset (1, 1)
            gl.glEnable (gl.GL_POLYGON_OFFSET_FILL)
            cube.draw( gl.GL_QUADS, 'pn' )
        gl.glDisable (gl.GL_LIGHTING)
        gl.glDisable (gl.GL_POLYGON_OFFSET_FILL)
        gl.glEnable (gl.GL_LINE_SMOOTH)
        gl.glEnable (gl.GL_BLEND)                     
        gl.glDepthMask (gl.GL_FALSE)
        gl.glColor4f(0,0,0,.5)
        gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_LINE )
        cube.draw( gl.GL_QUADS, 'p' )
        gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_FILL )
        gl.glDepthMask (gl.GL_TRUE)

    def on_init():
        gl.glEnable (gl.GL_LIGHT0)
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_AMBIENT,  (0.1, 0.1, 0.1, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_POSITION, (0.0, 1.0, 2.0, 1.0))
        gl.glEnable (gl.GL_BLEND)
        gl.glEnable (gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def on_draw():
        fig.clear()
        draw_background()
        trackball.push()
        draw_scene()
        trackball.pop()

    def on_mouse_drag(x, y, dx, dy, button):
        trackball.drag_to(x,y,dx,dy)
        bar.update()
        fig.redraw()

    def on_mouse_scroll(x, y, dx, dy):
        trackball.zoom_to(x,y,3*dx,3*dy)
        bar.update()
        fig.redraw()

    def on_key_press(symbol, modifiers):
        if symbol == glumpy.window.key.ESCAPE:
            sys.exit()



    fig.window.push_handlers(on_init,
                             on_mouse_drag,
                             on_mouse_scroll,
                             on_key_press)
    fig.window.push_handlers(atb.glumpy.Handlers(fig.window))
    fig.window.push_handlers(on_draw)
    glumpy.show()



