# coding: utf-8
# Copyright (C) 2011 Frank Broniewski <frank.broniewski@gmail.com>

# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA


from nose.tools import eq_
import mapscript
from msjson.datatypes import *


def test_boolean():
    class C(object):
        foo = Boolean('antialias')
        def __init__(self):
            self.mapscript = mapscript.labelObj()
            self.mapscript.antialias = mapscript.MS_TRUE
    
    c = C()
    eq_(c.foo, True)
    c.foo = False
    eq_(c.foo, False)
    eq_(c.mapscript.antialias, mapscript.MS_FALSE)


def test_status():
    class C(object):
        foo = Status('status')
        def __init__(self):
            self.mapscript = mapscript.layerObj()
            self.mapscript.status = mapscript.MS_ON

    c = C()
    eq_(c.foo, 'on')
    c.foo = 'off'
    eq_(c.foo, 'off')
    eq_(c.mapscript.status, mapscript.MS_OFF)


def test_unit():
    class C(object):
        foo = Unit('units')
        def __init__(self):
            self.mapscript = mapscript.mapObj()
            self.mapscript.units = mapscript.MS_DD
    c = C()
    eq_(c.foo, 'dd')
    c.foo = 'meter'
    eq_(c.foo, 'meter')
    eq_(c.mapscript.units, mapscript.MS_METERS)


def test_layer_type():
    class C(object):
        foo = LayerType('type')
        def __init__(self):
            self.mapscript = mapscript.layerObj()
            self.mapscript.type = mapscript.MS_LAYER_POINT

    c = C()
    eq_(c.foo, 'point')
    c.foo = 'line'
    eq_(c.foo, 'line')
    eq_(c.mapscript.type, mapscript.MS_LAYER_LINE)


def test_position():
    class C(object):
        foo = Position('position')
        def __init__(self):
            self.mapscript = mapscript.labelObj()
            self.mapscript.position = mapscript.MS_UL

    c = C()
    eq_(c.foo, 'ul')
    c.foo = 'lr'
    eq_(c.foo, 'lr')
    eq_(c.mapscript.position, mapscript.MS_LR)

def test_imagemode():
    class C(object):
        foo = ImageMode('imagemode')
        def __init__(self):
            self.mapscript = mapscript.outputFormatObj('AGG/PNG')
            self.mapscript.imagemode = mapscript.MS_IMAGEMODE_RGB

    c = C()
    eq_(c.foo, 'rgb')
    c.foo = 'rgba'
    eq_(c.foo, 'rgba')
    eq_(c.mapscript.imagemode, mapscript.MS_IMAGEMODE_RGBA)
