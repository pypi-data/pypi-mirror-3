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
from msjson.types import *


def get_class():
    c = mapscript.classObj()
    c.keyimage = u'bär.png'.encode('cp1252')
    c.maxscale = 6543.21
    c.debug = 0
    c.setExpression(u"[Mat] eq 'Grès' and [Catégorie] eq '1'".encode('cp1252'))
    c.setText(u'°²²³'.encode('cp1252'))
    return c


def get_map():
    png = mapscript.outputFormatObj('AGG/PNG', 'png32')
    gd = mapscript.outputFormatObj('GD/GIF', 'gif')
    m = mapscript.mapObj()
    m.appendOutputFormat(png)
    m.appendOutputFormat(gd)
    m.selectOutputFormat('png32')
    m.setProjection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    m.setSize(500,500)
    return m


def test_expression():
    class C(object):
        e = Expression(mapfile_encoding='cp1252')
        def __init__(self):
            self.mapscript = get_class()
  
    # getExpressionString() : string
    # Return a string representation of the expression enclosed in the quote 
    # characters appropriate to the expression type.
    # expr = '"%s"' % "[Mat] eq 'Grès' and [Catégorie] eq '1'"
    expr = u'"%s"' % u"[Mat] eq 'Grès' and [Catégorie] eq '1'"
    c = C()
    eq_(c.e, expr)
    c.e = u'"%s"' % u"[Mat] eq 'Grès'"
    eq_(c.e, u'"%s"' % u"[Mat] eq 'Grès'")


def test_float():
    class C(object):
        foo = Float('maxscale')
        def __init__(self):
            self.mapscript = get_class()

    c = C()
    eq_(c.foo, 6543.21)
    c.foo = 9876.54321
    eq_(c.foo, 9876.54321)
    eq_(c.mapscript.maxscale, 9876.54321)


def test_imagetype():
    class C(object):
        i = ImageType(mapfile_encoding='cp1252')
        def __init__(self):
            self.mapscript = get_map()

    c = C()
    eq_(c.i, 'png32')
    c.i = 'gif'
    eq_(c.i, 'gif')


def test_integer():
    class C(object):
        i = Integer('debug')
        def __init__(self):
            self.mapscript = get_class()

    c = C()
    eq_(c.i, 0)
    c.i = 3
    eq_(c.mapscript.debug, 3)
    eq_(c.i, 3)


def test_projection():
    class C(object):
        p = Projection(mapfile_encoding='cp1252')
        def __init__(self):
            self.mapscript = get_map()

    c = C()
    eq_(c.p, u'+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    c.p = u'+proj=tmerc +lat_0=49.83333333333334 +lon_0=6.166666666666667 +k=1 +x_0=80000 +y_0=100000 +ellps=intl +towgs84=-193,13.7,-39.3,-0.41,-2.933,2.688,0.43 +units=m +no_defs'
    eq_(c.p, u'+proj=tmerc +lat_0=49.83333333333334 +lon_0=6.166666666666667 +k=1 +x_0=80000 +y_0=100000 +ellps=intl +towgs84=-193,13.7,-39.3,-0.41,-2.933,2.688,0.43 +units=m +no_defs')


def test_size():
    class C(object):
        s = Size()
        def __init__(self):
            self.mapscript = get_map()

    c = C()
    eq_(c.s, (500,500))
    c.s = [600,600]
    eq_(c.s, (600,600))


def test_string():
    class C(object):
        foo = String('keyimage', 'cp1252')
        def __init__(self):
            self.mapscript = get_class()

    c = C()
    eq_(c.foo, u'bär.png')
    c.foo = u'föö.png'
    eq_(c.foo, u'föö.png')
    eq_(c.mapscript.keyimage, u'föö.png'.encode('cp1252'))
    c.foo = u'ààà.png'
    eq_(c.foo, u'ààà.png')
    eq_(c.mapscript.keyimage, u'ààà.png'.encode('cp1252'))


def test_text():
    class C(object):
        t = Text(mapfile_encoding='cp1252')
        def __init__(self):
            self.mapscript = get_class()

    c = C()
    eq_(c.t, u'°²²³')
    c.t = u'foo'
    eq_(c.t, u'foo')
