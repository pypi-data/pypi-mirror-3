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

xyz  = np.dtype( [('x','f4'), ('y','f4'), ('z','f4')] )
rgba = np.dtype( [('r','f4'), ('g','f4'), ('b','f4'), ('a','f4')] )
uv   = np.dtype( [('u','f4'), ('v','f4')] )

v = np.zeros( (5,5), dtype = [ ('position',        xyz),
                               ('color',           rgba),
                               ('normal',          xyz),
                               ('tex_coord',       uv),
                               ('edge_flag',       'f4'),
                               ('secondary_color', rgba),
                               ('fog_coord',       uv) ] )


V = v.view( dtype = [ ('position',        'f4', 3),
                      ('color',           'f4', 4),
                      ('normal',          'f4', 3),
                      ('tex_coord',       'f4', 2),
                      ('edge_flag',       'f4', 1),
                      ('secondary_color', 'f4', 4),
                      ('fog_coord',       'f4', 2) ] )

v['position']['y'][0,0] = 1.2345
print V['position'][0,0,1]
