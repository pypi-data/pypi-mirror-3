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
    Holds the most basic mapscript object handlers. Basic in terms of their
    properties, not their *simpleness*. The handlers themselves do not have
    :ref:`module-types` or :ref:`module-datatypes` properties. They just return 
    or receive JSON objects.
"""

import inspect
import sys
import mapscript
from msjson.types import Property



class Base(Property):
    """
    The Base Class for all Mapserver JSON objects
    
    Can either be used as a descriptor on other classes or as a standalone
    version. Inherits from :ref:`class-property`.
    """

    base = None

    def __init__(self, property_name=None, mapscript_=None, json=None, init_param=None,
                 mapfile_encoding=None):
        """
        :param property_name: Mapscript property name.
        
            holds the property name of the mapscripts' object property,
            e.g. :attr:`name` for :class:`mapscript.mapObj` . :attr:`name`. 
            This is used in conjunction with getattr and setattr for setting
            and retrieving values to and from a mapscript object.

        :param mapscript_: mapscript object
            
            holds the mapscript object for json serialisation

        :param json: json object

            holds the json object for direct instatiation from a json object.

        :param init_param: mapscript object instantiation parameter

            holds eventually necessary instatiation parameters of mapscript
            objects. At the moment it is only useful for
            :class:`mapscript.outputFormatObj` as this class takes the driver
            name on instanciation.

        :param mapfile_encoding: Encoding of mapfile.

            holds the encoding name of the mapfile encoding. Gets usually
            copied from the parent instance. Only the first class defines this
            and each subclass tries to copy the value from its parent class.

        """
        Property.__init__(self, property_name, mapfile_encoding)

        self.mapscript = mapscript_
        self.json = json
        self.init_param = init_param

        if self.json is not None:
            self.from_json(self.json)

        if self.mapscript is None:
            self._create_empty_mapscript()

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
#        self.mapscript = self._getattr(self.instance_mapscript, self.property_name)
        self.mapscript = self._getattr()
        return self.to_json()

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
#        self.mapscript = self._getattr(self.instance_mapscript, self.property_name)
        self.mapscript = self._getattr()
        self.from_json(value)

    def _create_empty_mapscript(self):
        """Create a new mapscript object of type "base" on self.mapscript"""
        if self.init_param is not None:
            self.mapscript = self.base(self.init_param)
        else:
            self.mapscript = self.base()
    
    def _properties(self):
        properties = list()
        for name, cls in inspect.getmembers(type(self), 
                                            lambda x: isinstance(x, Property)):
            if not name.startswith('_'):
                properties.append(name)
        return properties

    def to_json(self):
        """Return a jsonified version of self"""
        return dict([(p, getattr(self, p)) for p in self._properties()])

    def from_json(self, json):
        """Initialise self from a jsonified version"""
        for key, value in json.iteritems():
            setattr(self, key, value)



class Color(Base):
    """
    A Color object property
    
    Handles :class:`mapscript.colorObj` objects. The JSON representation 
    of :ref:`class-color` is::

        {
            'red': [-1, 0-255],
            'green': [-1, 0-255],
            'blue': [-1, 0-255]
        }

    The values in square brackets indicate possible values, where -1 means not
    set and 0-255 is the possible value range.
    """

    base = mapscript.colorObj
    
    def to_json(self):
        # mapscript can be None if attribute does not exist on instance
        if self.mapscript is None:
            return None
        return {'red': self.mapscript.red, 'green': self.mapscript.green,
                'blue': self.mapscript.blue}

    def from_json(self, json):
        if self.mapscript is None:
            self._create_empty_mapscript()
        if json is not None:
            self.mapscript.setRGB(json['red'], json['green'], json['blue'])



class HashTable(Base):
    """
    A HashTable object
    
    Handles :class:`mapscript.hashTableObj` objects. The JSON representation
    is a flat, not nested :func:`dict`.
    """

    base = mapscript.hashTableObj

    def to_json(self):
        json = dict()
        if self.mapscript is None:
            return json
        key = self.mapscript.nextKey(None)
        while key:
            json[self.decode(key)] = self.decode(self.mapscript.get(key))
            key = self.mapscript.nextKey(key)
        return json

    def from_json(self, json):
        if self.mapscript is None:
            self._create_empty_mapscript()
        self.mapscript.clear()
        for k, v in json.iteritems():
            self.mapscript.set(self.encode(k), self.encode(v))



class Rect(Base):
    """
    A rectObj (Extent)
    
    Handles :class:`mapscript.rectObj` objects. :class:`mapscript.rectObj`
    are primarily used on :class:`mapscript.mapObj` and
    :class:`mapscript.layerObj` objects to define the extent. The JSON 
    representation of :ref:`class-rect` is::

        {
            'minx': [-1, ..],
            'maxx': [-1, ..],
            'miny': [-1, ..],
            'maxy': [-1, ..]
        }

    The values in square brackets indicate possible values where -1 means not
    set and .. means any floating point number. Obviously the values for
    *minx* and *miny* should be smaller than the values for *maxx* and *maxy*.
    Otherwise the mapscript object will raise an error.
    """

    base = mapscript.rectObj

    def to_json(self):
        if self.mapscript is None:
            return None
        return {'maxx': self.mapscript.maxx, 'maxy': self.mapscript.maxy,
                'minx': self.mapscript.minx, 'miny': self.mapscript.miny}

    def from_json(self, json):
        if self.mapscript is None:
            self._create_empty_mapscript()
        if json is not None:
            self.mapscript.maxx = json['maxx']
            self.mapscript.maxy = json['maxy']
            self.mapscript.minx = json['minx']
            self.mapscript.miny = json['miny']
