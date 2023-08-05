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
Datatypes are a handler between 
`mapserver variables <http://mapserver.org/mapscript/variables.html>`_ 
and Python data types. In order to provide a consequent API between mapscript
and JSON, a :func:`dict` is used to map between both.

e.g.::

    Map(Base):
        # set a data type
        status = Status('status')

"""


import mapscript
from types import Property


class DataType(Property):
    """
    Represents mapscript variables

    see http://mapserver.org/mapscript/variables.html for a complete list of 
    available variables. Uses a mapping dict to transfer between mapscript
    variable value and python values.

    Inherits from :ref:`class-property`.
    """

    def __init__(self, property_name, mapfile_encoding=None):
        Property.__init__(self, property_name, mapfile_encoding)
        self._map = dict()
        self._inversed_map = None

    @property
    def _inverse_map(self):
        if not self._inversed_map:
            self._inversed_map = dict(zip(self._map.values(), self._map.keys()))
        return self._inversed_map

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        value = self._getattr()
        try:
            return self._inverse_map[value]
        except KeyError:
            return None

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
        try:
            self._setattr(self._map[value])
        except KeyError:
            pass



class Align(DataType):
    """
    Align data type

    Maps alignment properties to or from string representation.

    Alignments are:
    - 'left' : :attr:`mapscript.MS_ALIGN_LEFT`
    - 'center' : :attr:`mapscript.MS_ALIGN_CENTER`
    - 'right' : :attr:`mapscript.MS_ALIGN_RIGHT`
    - None : -1
    
    """

    def __init__(self, property_name, mapfile_encoding=None):
        DataType.__init__(self, property_name, mapfile_encoding)
        self._map = {
            'left' : mapscript.MS_ALIGN_LEFT,
            'center' : mapscript.MS_ALIGN_CENTER,
            'right' : mapscript.MS_ALIGN_RIGHT,
            None : -1
        }



class Boolean(DataType):
    """
    Boolean data type

    Maps :attr:`mapscript.MS_TRUE` and :attr:`mapscript.MS_FALSE` values to
    and from python boolean conditions. Additionally there's also a "not set"
    condition, represented by python's None and -1 for mapscript.
    """

    def __init__(self, property_name, mapfile_encoding=None):
        DataType.__init__(self, property_name, mapfile_encoding)
        self._map = {
            True : mapscript.MS_TRUE,
            False : mapscript.MS_FALSE,
            None : -1
        }




class Connection(DataType):
    """
    Connection data type

    maps a mapscript connection type to or from a string representation.
    Mapped connections are:

    - 'inline' : :attr:`mapscript.MS_INLINE`
    - 'shapefile' : :attr:`mapscript.MS_SHAPEFILE`
    - 'tiled_shapefile' : :attr:`mapscript.MS_TILED_SHAPEFILE`
    - 'sde' : :attr:`mapscript.MS_SDE`
    - 'ogr' : :attr:`mapscript.MS_OGR`
    - 'postgis' : :attr:`mapscript.MS_POSTGIS`
    - 'wms' : :attr:`mapscript.MS_WMS`
    - 'oracle' : :attr:`mapscript.MS_ORACLESPATIAL`
    - 'wfs' : :attr:`mapscript.MS_WFS`
    - 'graticule' : :attr:`mapscript.MS_GRATICULE`
    - 'raster' : :attr:`mapscript.MS_RASTER`

    """

    def __init__(self, property_name, mapfile_encoding=None):
        DataType.__init__(self, property_name, mapfile_encoding)
        self._map = {
            'inline' : mapscript.MS_INLINE,
            'shapefile' : mapscript.MS_SHAPEFILE,
            'tiled_shapefile' : mapscript.MS_TILED_SHAPEFILE,
            'sde' : mapscript.MS_SDE,
            'ogr' : mapscript.MS_OGR,
            'postgis' : mapscript.MS_POSTGIS,
            'wms' : mapscript.MS_WMS,
            'oracle' : mapscript.MS_ORACLESPATIAL,
            'wfs' : mapscript.MS_WFS,
            'graticule' : mapscript.MS_GRATICULE,
            'raster' : mapscript.MS_RASTER
        }




class Status(DataType):
    """
    Status data type
   
    Mapping:

    - 'on' : :attr:`mapscript.MS_ON`
    - 'off' : :attr:`mapscript.MS_OFF`
    - 'default' : :attr:`mapscript.MS_DEFAULT`
    - 'embed' : :attr:`mapscript.MS_EMBED`

    """

    def __init__(self, property_name, mapfile_encoding=None):
        DataType.__init__(self, property_name, mapfile_encoding)
        self._map = {
            'on' : mapscript.MS_ON,
            'off' : mapscript.MS_OFF,
            'default' : mapscript.MS_DEFAULT,
            'embed' : mapscript.MS_EMBED
        }




class Unit(DataType):
    """
    Unit data type
    
    Mapping:

    - 'dd' : :attr:`mapscript.MS_DD`
    - 'feet' : :attr:`mapscript.MS_FEET`
    - 'inch' : :attr:`mapscript.MS_INCHES`
    - 'meter' : :attr:`mapscript.MS_METERS`
    - 'miles' : :attr:`mapscript.MS_MILES`
    - 'nautical' : :attr:`mapscript.MS_NAUTICALMILES`
    - 'pixel' : :attr:`mapscript.MS_PIXELS`

    """

    def __init__(self, property_name, mapfile_encoding=None):
        DataType.__init__(self, property_name, mapfile_encoding)
        self._map = {
            'dd' : mapscript.MS_DD,
            'feet' : mapscript.MS_FEET,
            'inch' : mapscript.MS_INCHES,
            'meter' : mapscript.MS_METERS,
            'miles' : mapscript.MS_MILES,
            'nautical' : mapscript.MS_NAUTICALMILES,
            'pixel' : mapscript.MS_PIXELS
        }




class LayerType(DataType):
    """
    LayerType data type
    
   Mapping:

    - 'point' : :attr:`mapscript.MS_LAYER_POINT`
    - 'line' : :attr:`mapscript.MS_LAYER_LINE` 
    - 'polygon' : :attr:`mapscript.MS_LAYER_POLYGON`
    - 'raster' : :attr:`mapscript.MS_LAYER_RASTER`
    - 'annotation' :attr:`mapscript.MS_LAYER_ANNOTATION`
    - 'query' : :attr:`mapscript.MS_LAYER_QUERY`
    - 'circle' : :attr:`mapscript.MS_LAYER_CIRCLE`
    - 'tileindex' :attr:`mapscript.MS_LAYER_TILEINDEX`
    """
    
    def __init__(self, property_name, mapfile_encoding=None):
        DataType.__init__(self, property_name, mapfile_encoding)
        self._map = {
            'point' : mapscript.MS_LAYER_POINT,
            'line' : mapscript.MS_LAYER_LINE,
            'polygon' : mapscript.MS_LAYER_POLYGON,
            'raster' : mapscript.MS_LAYER_RASTER,
            'annotation' : mapscript.MS_LAYER_ANNOTATION,
            'query' : mapscript.MS_LAYER_QUERY,
            'circle' : mapscript.MS_LAYER_CIRCLE,
            'tileindex' : mapscript.MS_LAYER_TILEINDEX
        }




class Position(DataType):
    """
    Position data type

    Mapping:

    - 'ul' : :attr:`mapscript.MS_UL`
    - 'll' : :attr:`mapscript.MS_LL`
    - 'ur' : :attr:`mapscript.MS_UR`
    - 'lr' : :attr:`mapscript.MS_LR`
    - 'cl' : :attr:`mapscript.MS_CL`
    - 'cr' : :attr:`mapscript.MS_CR`
    - 'uc' : :attr:`mapscript.MS_UC`
    - 'lc' : :attr:`mapscript.MS_LC`
    - 'cc' : :attr:`mapscript.MS_CC`
    - 'auto' : :attr:`mapscript.MS_AUTO`
    - None : 111

    """

    def __init__(self, property_name, mapfile_encoding=None):
        DataType.__init__(self, property_name, mapfile_encoding)
        self._map = {    
            'ul' : mapscript.MS_UL,
            'll' : mapscript.MS_LL,
            'ur' : mapscript.MS_UR,
            'lr' : mapscript.MS_LR,
            'cl' : mapscript.MS_CL,
            'cr' : mapscript.MS_CR,
            'uc' : mapscript.MS_UC,
            'lc' : mapscript.MS_LC,
            'cc' : mapscript.MS_CC,
            'auto' : mapscript.MS_AUTO,
            None : 111
        }




class ImageMode(DataType):
    """
    ImageMode data type
    
    Mapping:

    - 'pc256' : :attr:`mapscript.MS_IMAGEMODE_PC256`
    - 'rgb' : :attr:`mapscript.MS_IMAGEMODE_RGB`
    - 'rgba' : :attr:`mapscript.MS_IMAGEMODE_RGBA`
    - 'int16' : :attr:`mapscript.MS_IMAGEMODE_INT16`
    - 'float32' : :attr:`mapscript.MS_IMAGEMODE_FLOAT32`
    - 'byte' : :attr:`mapscript.MS_IMAGEMODE_BYTE`
    - 'null' : :attr:`mapscript.MS_IMAGEMODE_NULL`
  
    """

    def __init__(self, property_name, mapfile_encoding=None):
        DataType.__init__(self, property_name, mapfile_encoding)
        self._map = {
            'pc256' : mapscript.MS_IMAGEMODE_PC256,
            'rgb' : mapscript.MS_IMAGEMODE_RGB,
            'rgba' : mapscript.MS_IMAGEMODE_RGBA,
            'int16' : mapscript.MS_IMAGEMODE_INT16,
            'float32' : mapscript.MS_IMAGEMODE_FLOAT32,
            'byte' : mapscript.MS_IMAGEMODE_BYTE,
            'null' : mapscript.MS_IMAGEMODE_NULL,
        }
