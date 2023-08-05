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


"""
This module contains only classes that do not have other mapscript
classes as property but only types, datatypes and base classes.
For a full list of properties the
`mapscript manual <http://mapserver.org/mapscript/mapscript.html>`_
can be consulted.

e.g.::

    Map(Base):
        legend = Legend('legend')

"""


import mapscript
from msjson.types import Float, Integer, String 
from msjson.datatypes import Align, Boolean, ImageMode, Position, Status, Unit
from msjson.base import Base, Color, HashTable, Rect



class FontSet(Base):
    """
    A FontSet object

    Handles :class:`mapscript.fontSetObj` objects.

    .. warning::
        
        This is currently broken. Trying to access the
        :class:`mapscript.fontSetObj` . :attr:`fonts` property results in a
        segmentation fault on the mapscript side.


    """
    base = mapscript.fontSetObj

    filename = String('filename')
    fonts = HashTable('fonts')




class Label(Base):
    """
    A Label object

    Handles :class:`mapscript.labelObj` objects. A label is usually a
    property of :ref:`class-class` objects.

    e.g.::
        
        Class(Base):
            label = Label('label')

    """
    base = mapscript.labelObj
    
    angle = Float('angle')
    antialias = Boolean('antialias')
    autoangle = Boolean('autoangle')
    autofollow = Boolean('autofollow')
    autominfeaturesize = Boolean('autominfeaturesize')
    backgroundcolor = Color('backgroundcolor')
    backgroundshadowcolor = Color('backgroundshadowcolor')
    backgroundshadowsizex = Integer('backgroundshadowsizex')
    backgroundshadowsizey = Integer('backgroundshadowsizey')
    buffer = Integer('buffer')
    color = Color('color')
    encoding = String('encoding')
    font = String('font')
    force = Boolean('force')
    maxlength = Integer('maxlength')
    maxscaledenom = Float('maxscaledenom')
    maxsize = Integer('maxsize')
    mindistance = Integer('mindistance')
    minfeaturesize = Integer('minfeaturesize')
    minlength = Integer('minlength')
    minscaledenom = Integer('minscaledenom')
    minsize = Integer('minsize')
    offsetx = Integer('offsetx')
    offsety = Integer('offsety')
    outlinecolor = Color('outlinecolor')
    outlinewidth = Integer('outlinewidth')
    partials = Boolean('partials')
    position = Position('position')
    priority = Integer('priority')
    shadowcolor = Color('shadowcolor')
    shadowsizex = Integer('shadowsizex')
    shadowsizey = Integer('shadowsizey')
    size = Integer('size')
    wrap = String('wrap')



class Legend(Base):
    """
    A Legend object

    Handles :class:`mapscript.legendObj` objects. A legend is usually attached
    to a Map objects legend attribute.

    e.g.::
        
        Map(Base):
            legend = Legend('legend')

    """
    base = mapscript.legendObj

    height = Integer('height')
    imagecolor = Color('imagecolor')
    keysizex = Integer('keysizex')
    keysizey = Integer('keysizey')
    keyspacingx = Integer('keyspacingx')
    keyspacingy = Integer('keyspacingy')
    label = Label('label')
    outlinecolor = Color('outlinecolor')
    position = Position('position')
    postlabelcache = Boolean('postlabelcache')
    status = Status('status')
    template = String('template')
    width = Integer('width')



class OutputFormat(Base):
    """
    An OutputFormat object

    Handles :class:`mapscript.outputFormatObj` objects. An OutputFormat object
    can be used to obtain the :attr:`outputformat` attribute of the
    :class:`mapscript.mapObj` object. And it should be part of the 
    :attr:`outputformatlist` attribute of the :class:`mapscript.outputFormatObj`
    object. The 
    `manual <http://mapserver.org/mapscript/mapscript.html#mapobj>`_ notes for
    the :attr:`outputformatlist`:

    .. note::
        
        outputformatlist : outputFormatObj[]
        Array of the available output formats.

        Note: Currently only available for C#. A proper typemaps should be
        implemented for the other languages.

    So obtaining a list of outputformats is currently not possible. While it is
    possible to obtain the number of outputformats registered for a map there
    exists no possibility to iterate over the outputformats, there's only a 
    getter method (:meth:`getOutputFormatByName`) by name, not by index.

    e.g.::

        Map(Base):
            output_format = OutputFormat('outputformat')


    """
    base = mapscript.outputFormatObj

    driver = String('driver')
    extension = String('extension')
    imagemode = ImageMode('imagemode')
    mimetype = String('mimetype')
    name = String('name')
    transparent = Status('transparent')



class ScaleBar(Base):
    """
    A ScaleBar object

    Handles :class:`mapscript.scalebarObj` objects. A ScaleBar is usually
    attached to a :ref:`class-map` object.

    e.g.::

        Map(Base):
            scalebar = ScaleBar('scalebar')

    """
    base = mapscript.scalebarObj

    align = Align('align')
    backgroundcolor = Color('backgroundcolor')
    color = Color('color')
    height = Integer('height')
    imagecolor = Color('color')
    intervals = Integer('intervals')
    label = Label('label')
    outlinecolor = Color('outlinecolor')
    position = Position('position')
    postlabelcache = Boolean('postlabelcache')
    status = Status('status')
    style = Integer('style')
    units = Unit('units')
    width = Integer('width')



class Style(Base):
    """
    A Style object

    Handles :class:`mapscript.styleObj` objects. A Style is part of a 
    collection of Style objects attached to a :ref:`class-class` object and
    is normally not used directly. It can be used to jsonify a
    :class:`mapscript.styleObj` object though.

    e.g. in a :ref:`class-collection`::

        Class(Base):
            styles = Collection(Style, 'getStyle', 'removeStyle', 'insertStyle'
                                'numstyles')

    or as standalone::

        import mapscript
        import msjson

        ms_style = mapscript.styleObj()
        style = msjson.Style(mapscript_=ms_style)
        style.to_json()

    """
    base = mapscript.styleObj

    angle = Float('angle')
    antialias = Boolean('antialias')
    autoangle = Boolean('autoangle')
    backgroundcolor = Color('backgroundcolor')
    color = Color('color')
    gap = Float('gap')
    maxsize = Integer('maxsize')
    maxwidth = Integer('maxwidth')
    minsize = Integer('minsize')
    minwidth = Integer('minwidth')
    offsetx = Integer('offsetx')
    offsety = Integer('offsety')
    outlinecolor = Color('outlinecolor')
    size = Integer('size')
    symbol = Integer('symbol')
    width = Integer('width')



class Web(Base):
    """
    A Web object

    Handles :class:`mapscript.webObj` objects. A Web object is usually
    attached to a :ref:`class-map` object.

    e.g.::

        Map(Base):
            web = Web('web')

    """
    base = mapscript.webObj

    imagepath = String('imagepath')
    imageurl = String('imageurl')
    metadata = HashTable('metadata')
