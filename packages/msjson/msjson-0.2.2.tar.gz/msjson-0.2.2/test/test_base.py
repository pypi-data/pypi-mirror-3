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
from msjson.base import *


def test_color():
    class C(object):
        foo = Color('color')
        def __init__(self):
            self.mapscript = mapscript.labelObj()
            self.mapscript.color = mapscript.colorObj(10,10,10)

    jc = {'red': 10, 'green': 10, 'blue': 10}
    c = C()
    eq_(c.foo, jc)

    jc = {'red': 5, 'green': 5, 'blue': 5}
    c.foo = jc
    eq_(c.foo, jc)
    eq_(c.mapscript.color.red, 5)

    c = Color()
    c.from_json(jc)
    eq_(c.mapscript.red, jc['red'])

    jc = c.to_json()
    eq_(jc['red'], c.mapscript.red)


def test_hash():
    class C(object):
        foo = HashTable('metadata', mapfile_encoding='cp1252')
        def __init__(self):
            self.mapscript = mapscript.layerObj()
            self.mapscript.metadata.set(u'foo'.encode('cp1252'),
                                     u'bar'.encode('cp1252'))
            self.mapscript.metadata.set(u'hundert'.encode('cp1252'), 
                                     u'100'.encode('cp1252'))
            self.mapscript.metadata.set(u'Ümläut'.encode('cp1252'),
                                     u'énèrvé'.encode('cp1252'))

    jh_utf8 = {u'foo': u'bar', u'hundert': u'100', u'Ümläut': u'énèrvé'}
    
    c = C()
    eq_(c.foo, jh_utf8)

    c.foo = jh_utf8
    eq_(c.foo, jh_utf8)

    h = HashTable(mapfile_encoding='cp1252')
    h.from_json(jh_utf8)
    eq_(h.to_json()['foo'], jh_utf8['foo'])


def test_rect():
    class C(object):
        foo = Rect('extent')
        def __init__(self):
            self.mapscript = mapscript.mapObj()
            self.mapscript.setExtent(500,500,2000,2000)

    jr = {'maxx': 2000, 'maxy': 2000, 'minx': 500, 'miny': 500}
    c = C()
    eq_(c.foo, jr)
    
    jr = {'maxx': 1000, 'maxy': 1000, 'minx': 100, 'miny': 100}
    c.foo = jr
    eq_(c.foo, jr)
    eq_(c.mapscript.extent.minx, 100)

    r = Rect()
    r.from_json(jr)
    eq_(r.mapscript.minx, jr['minx'])
    jr = r.to_json()
    eq_(jr['minx'], r.mapscript.minx)
