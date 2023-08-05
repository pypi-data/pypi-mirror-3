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
This module contains the three most advanced classes for dealing with 
:class:`mapscript.classObj`, :class:`mapscript.layerObj` and
:class:`mapscript.mapObj` objects. All of these have a property of type
:ref:`class-collection` for dealing with their list like child elements.

e.g.::

    Class(Base):
        debug = Integer('debug')
        # ... other properties
        styles = Collection(Style, 'getStyle', 'removeStyle', 'insertStyle',
                            'numstyles'


"""


import mapscript
from msjson.types import Collection, Expression, Float, ImageType, Integer,\
                         Projection, Property, Size, String, Text
from msjson.datatypes import Boolean, Connection, LayerType, Status, Unit
from msjson.base import Base, Color, HashTable, Rect
from msjson.baseclasses import FontSet, Label, Legend, OutputFormat,\
                               ScaleBar, Style, Web



class Class(Base):
    """
    A Class object

    Handles :class:`mapscript.classObj` objects.

    e.g.::

        Class(Base):
            debug = Integer('debug')
            # ... other properties
            styles = Collection(Style, 'getStyle', 'removeStyle', 'insertStyle',
                                'numstyles'
   
    """
    base = mapscript.classObj

    debug = Integer('debug')
    expression = Expression()
    keyimage = String('keyimage')
    label = Label('label')
    maxscaledenom = Float('maxscaledenom')
    metadata = HashTable('metadata')
    minscaledenom = Float('minscaledenom')
    name = String('name')
    status = Status('status')
    template = String('template')
    title = String('title')
    text = Text()

    styles = Collection(Style, 'getStyle', 'removeStyle', 'insertStyle',
                        'numstyles')



class Layer(Base):
    """
    A Layer object

    Handles :class:`mapscript.layerObj` objects

    e.g.::
        
        Layer(Base):
            name = String('name')
            # ... other properties
            classes = Collection(Class, 'getClass', 'removeClass',
                                 'insertClass', 'numclasses')

    """
    base = mapscript.layerObj

    bandsitem = String('bandsitem')
    classgroup = String('classgroup')
    classitem = String('classitem')
    connection = String('connection')
    connectiontype = Connection('connectiontype')
    data = String('data')
    debug = Integer('debug')
    dump = Boolean('dump')
    extent = Rect('extent')
    filteritem = String('filteritem')
    footer = String('footer')
    group = String('group')
    header = String('header')
    labelcache = Boolean('labelcache')
    labelitem = String('labelitem')
    labelmaxscale = Float('labelmaxscaledenom')
    labelminscale = Float('labelminscaledenom')
    labelrequires = String('labelrequires')
    maxscale = Float('maxscaledenom')
    metadata = HashTable('metadata')
    minscale = Float('minscaledenom')
    name = String('name')
    offsite = Color('offsite')
    opacity = Integer('opacity')
    requires = String('requires')
    sizeunits = Unit('sizeunits')
    status = Status('status')
    styleitem = String('styleitem')
    symbolscale = Float('symbolscaledenom')
    template = String('template')
    tileindex = String('tileindex')
    tileitem = String('tileitem')
    tolerance = Float('tolerance')
    toleranceunits = Unit('toleranceunits')
    transform = Boolean('transform')
    type = LayerType('type')
    units = Unit('units')
    
    classes = Collection(Class, 'getClass', 'removeClass', 'insertClass',
                         'numclasses')



class Map(Base):
    """
    A Map object

    Handles :class:`mapscript.mapObj` objects. This is the top level object
    in the mapscript hierarchy.

    e.g.::

        Map(Base):
            name = String('name')
            # ... other properties
            layers = Collection(Layer, 'getLayer', 'removeLayer',
                                'insertLayer', 'numlayers')

    """
    base = mapscript.mapObj

    cellsize = Float('cellsize')
    # TODO: Missed this class it seems, subset of Hashtable
#    configoptions = ConfigOptions('configoptions')
    datapattern = String('datapattern')
    debug = Integer('debug')
    extent = Rect('extent')
    # fontset does not work currently
#    fontset = FontSet('fontset')
    imagecolor = Color('imagecolor')
    legend = Legend('legend')
    mappath = String('mappath')
    maxsize = Integer('maxsize')
    name = String('name')
    outputformat = OutputFormat('outputformat', init_param='AGG/PNG')
    projection = Projection('projection')
    # TODO: Missed this class it seems -> create
#    reference = ReferenceMap('reference')
    resolution = Float('resolution')
    scalebar = ScaleBar('scalebar')
    scaledenom = Float('scaledenom')
    shapepath = String('shapepath')
    size = Size()
    templatepattern = String('templatepattern')
    units = Unit('units')
    web = Web('web')

    layers = Collection(Layer, 'getLayer', 'removeLayer', 'insertLayer',
                        'numlayers')
