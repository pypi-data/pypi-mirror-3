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


try:
    import json
except ImportError:
    import simplejson as json
import os
from nose.tools import eq_
import mapscript
from msjson.classes import *



def get_mapfile():
    mapfile = os.path.join(os.path.dirname(__file__), 'test.map')
    return mapscript.mapObj(mapfile)


def get_style():
    s = mapscript.styleObj()
    s.color = mapscript.colorObj(0,0,0)
    s.maxsize = 5
    s.angle = 10.0
    s.name = 'foo'
    return s


def test_class():
    msm = get_mapfile()
    msl = msm.getLayer(0)
    msc = msl.getClass(0)
    c = Class(mapscript_=msc, mapfile_encoding='cp1252')

    eq_(c.name, "200m - 300m")
    c.name = u'Füübör'
    eq_(c.name, u'Füübör')

    jc = c.to_json()
    new_c = Class(mapfile_encoding='cp1252')
    new_c.from_json(jc)


# segfaults
#def test_fontset():
#    curr_path = os.path.dirname(__file__)
#    msf = mapscript.fontSetObj()
#    msf.filename = 'fonts.map'
#    msf.fonts.set('xyz', os.path.join(curr_path, 'DejaVuSans.ttf'))
#    msf.fonts.set('courier', 'courier.ttf')


def test_map():
    msm = get_mapfile()
    
    m = Map(mapscript_=msm, mapfile_encoding='cp1252')
    eq_(m.name, u'pndö')
    eq_(len(m.layers), 30)

    jm = {u'name': u'féébàr'}
    m = Map(mapfile_encoding='cp1252')
    m.from_json(jm)
    eq_(m.name, u'féébàr')

    m = Map(mapscript_=msm, mapfile_encoding='cp1252')
    jm = m.to_json()
    m.from_json(jm)


def test_label():
    msm = get_mapfile()
    msl = msm.getLayerByName('villages-label')
    msc = msl.getClass(0)

    l = Label(mapscript_=msc.label, mapfile_encoding='cp1252')
    eq_(l.antialias, True)
    eq_(l.encoding, u'ISO-8859-1')


def test_layer():
    msm = get_mapfile()
    msl = msm.getLayer(0)

    l = Layer(mapscript_=msl)
    eq_(l.name, 'relief')
    eq_(l.dump, False)
    eq_(l.type, 'raster')

    jl = l.to_json()
    new_l = Layer(mapfile_encoding='cp1252')
    new_l.name = 'Foo'
    eq_(new_l.mapscript.name, u'Foo'.encode('cp1252'))
    new_l.from_json(jl)

    eq_(l.name, 'relief')
    eq_(l.dump, False)
    eq_(l.type, 'raster')


def test_legend():
    msm = get_mapfile()
    msl = msm.legend

    l = Legend(mapscript_=msl, mapfile_encoding='cp1252')
    eq_(l.keysizex, 16)

    # returns a json version of label
    label = l.label
    eq_(label['size'], 8)


def test_outputformat():
    msm = get_mapfile()
    mso = msm.outputformat

    o = OutputFormat(mapscript_=mso, mapfile_encoding='cp1252')
    eq_(o.name, 'png32')

    o = OutputFormat(mapfile_encoding='cp1252', init_param='AGG/PNG')
    o.name = 'foo'
    eq_(o.name, 'foo')


def test_scalebar():
    msm = get_mapfile()
    mss = msm.scalebar

    s = ScaleBar(mapscript_=mss)
    eq_(s.style, 0)


def test_style():
    mss = get_style() 
    s = Style(mapscript_=mss, mapfile_encoding='cp1252')
    sj = s.to_json()
    eq_(sj[u'angle'], 10.0)
    eq_(sj[u'color'], {'red':0, 'green':0, 'blue':0})


def test_web():
    msm = get_mapfile()
    msw = msm.web

    w = Web(mapscript_=msw)
    eq_(w.imagepath, '/usr/local/www/mapserver')
