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
    Types represent the most basic values. They map strings, numbers and
    certain mapserver specific types to and from python values.

    e.g.::

        Map(Base):
            name = String('name')
            res = Float('resolution')
            height = Integer('height')

"""


import sys
import warnings
import mapscript


class Property(object):
    """
        Property base class

        Implements the Descriptor pattern. This should be the base for new
        mapscript class properties.

    """

    def __init__(self, property_name=None, mapfile_encoding=None):
        """
        :param property_name: Mapscript property name.
        
            holds the property name of the mapscripts' object property,
            e.g. :attr:`name` for :class:`mapscript.mapObj` . :attr:`name`. 
            This is used in conjunction with getattr and setattr for setting
            and retrieving values to and from a mapscript object.

        :param mapfile_encoding: Encoding of mapfile.

            holds the encoding name of the mapfile encoding. Gets usually
            copied from the parent instance. Only the first class defines this
            and each subclass tries to copy the value from its parent class.
        """
        self.property_name = property_name
        self.mapfile_encoding = mapfile_encoding
        self.json_encoding = 'utf-8'
        self.instance_mapscript = None

    def __get__(self, instance, owner):
        """__get__ always returns a json representation of the Property"""
        if instance is None:
            return self
        self.instance_mapscript = self._get_mapscript_object(instance)
        self._copy_mapfile_encoding(instance)

    def __set__(self, instance, value):
        """__set__ sets the property from a json representation of the 
        Property"""
        self.instance_mapscript = self._get_mapscript_object(instance)
        self._copy_mapfile_encoding(instance)

    def _get_mapscript_object(self, instance):
        """Returns the mapscript object from instance"""
        return getattr(instance, 'mapscript')

    def _copy_mapfile_encoding(self, instance):
        """Copy instances mapfile_encoding value to self"""
        try:
            self.mapfile_encoding = instance.mapfile_encoding
        except AttributeError:
            pass

    def _getattr(self):
        """Get property from instance_mapscript or raise warning if 
        property does not exist on the mapscript object"""
        try:
            return getattr(self.instance_mapscript, self.property_name)
        except AttributeError:
            self._warning(self.instance_mapscript, self.property_name)
            return None

    def _setattr(self, value):
        """Set a property value on instance_mapscript or raise a warning
        if property does not exist on the mapscript object"""
        try:
            setattr(self.instance_mapscript, self.property_name, value)
        except AttributeError:
            self._warning(self.instance_mapscript, self.property_name)

    def _warning(self, instance, property_):
        """issue a warning, that property does not exist on the mapscript
        object"""
        warnings.warn("%s does not exist on %s, returning None" % 
                      (property_, instance), DeprecationWarning)

    def decode(self, value):
        """Try to decode a string from mapfile encoding to unicode.
        If no :attr:`mapfile_encoding` is defined the value is returned
        directly. If decoding with :attr:`mapfile_encoding` fails the 
        value from the mapscript object is returned directly."""
        if self.mapfile_encoding is None:
            return value
        try:
            return value.decode(self.mapfile_encoding)
        except (UnicodeDecodeError, AttributeError):
            return value

    def encode(self, value):
        """Try to encode a unicode string from json encoding to mapfile
        encoding. If no :attr:`mapfile_encoding` is defined the value is
        returned directly. If encoding with :attr:`mapfile_encoding` fails
        the value from JSON is returned directly."""
        if self.mapfile_encoding is None:
            return value
        try:
            return value.encode(self.mapfile_encoding)
        except (UnicodeEncodeError, AttributeError):
            return value



class Collection(Property):
    """
    Represents a collection of child elements of a mapscript object. The
    intended use is for layers in a map object, classes in a layer object 
    or styles in a class object.

    e.g.::
        
        layers = Collection('getLayer', 'removeLayer', 'insertLayer',
                            'numlayers')
    
    The JSON representation of the collection is a list of jsonified child
    items.
    """

    def __init__(self, base, get, remove, insert, numitems):
        """
        :param base: Base class for the collection.
            
            The base class of the collecion is usually any of :ref:`class-layer`, 
            :ref:`class-class` or :ref:`class-style`.

            New instances of base are created while reading the child objects
            from the descriptor instance and are converted to/from json.

        :param get: Name of the mapscript function for retrieval.

            This is :meth:`getLayer`, :meth:`getClass` or :meth:`getStyle` of 
            the corresponding mapscript object. Pass the name as
            :func:`string`.

        :param remove: Name of the mapscript function for removal.

            This is :meth:`removeLayer`, :meth:`removeClass` or 
            :meth:`removeStyle` of the corresponding mapscript object. Pass 
            the name as :func:`string`.

        :param insert: Name of the mapscript function for inserting.

            This is :meth:`insertLayer`, :meth:`insertClass` or 
            :meth:`insertStyle` of the corresponding mapscript object. Pass 
            the name as :func:`string`.

        :param numitems: Name of the attribute for the number of items.

            This is :attr:`numlayer`, :attr:`numclasses` or :attr:`numstyles`
            of the corresponding mapscript object. Pass the name as
            :func:`string`.
        """
        Property.__init__(self, None, None)
        self.baseclass = base
        self.func_name_get = get
        self.func_name_remove = remove
        self.func_name_insert = insert
        self.numitems_attr = numitems

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        func = getattr(self.instance_mapscript, self.func_name_get)
        numitems = getattr(self.instance_mapscript, self.numitems_attr)
        items = list()

        for item in self.iter(func, numitems):
            # prepare parameter for __init__
            params = {'mapscript_': item,
                      'mapfile_encoding': self.mapfile_encoding}
            cls = self.baseclass(**params)
            items.append(cls.to_json())
        return items

    def __set__(self, instance, values):
        Property.__set__(self, instance, values)

        insert = getattr(self.instance_mapscript, self.func_name_insert)
        remove = getattr(self.instance_mapscript, self.func_name_remove)
        numitems = getattr(self.instance_mapscript, self.numitems_attr)

        # remove existing items from instance before inserting the new ones
        # indexes are renamed after removing a layer from the map
        # so you only need to always remove the first one
        for index in xrange(numitems):
            remove(0)
    
        # add new values from json list
        for value in values:
            params = {'mapfile_encoding': self.mapfile_encoding}
            item = self.baseclass(**params)
            item.from_json(value)
            insert(item.mapscript)
    
    def iter(self, func, numitems):
        index = 0
        
        for index in xrange(numitems):
            item = func(index)
            yield item



class Expression(Property):
    """
    Class for mapping Mapserver expressions to and from JSON.
    :meth:`getExpressionString` and :meth:`setExpression` are used on 
    :class:`mapscript.classObj` to retrieve the expression.

    e.g.::

        CLASS
            EXPRESSION ("[DESCRIPTIO]" == "Naturelle")
        END

    """

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        return self.decode(self.instance_mapscript.getExpressionString())

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
        self.instance_mapscript.setExpression(self.encode(value))



class Float(Property):
    """
    Class for mapping float numeric values to and from JSON.
    """

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        value = self._getattr()
        if value is not None:
            return float(value)

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
        try:
            self._setattr(float(value))
        except TypeError:
            self._setattr(value)



class ImageType(Property):
    """
    Class for retrieving the imagetype from :class:`mapObj`.

    .. warning::

        Setting this is currently not fully functional. Problems arise if
        the output formats are not set on the mapscript object, but 
        :class:`ImageType` tries to set one which (yet) does not exist.

    e.g.::

        MAP
            IMAGETYPE "png32"
        END

    """

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        return self.decode(self.instance_mapscript.imagetype)

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
        self.instance_mapscript.selectOutputFormat(self.encode(value)) 



class Integer(Property):
    """
    Class for mapping integer values to and from JSON.
    """

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        value = self._getattr() 
        if value is not None:
            return int(value)

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
        try:
            self._setattr(int(value))
        except TypeError:
            self._setattr(value)



class Projection(Property):
    """
    Class for getting and setting the projection string on the mapscript
    :class:`mapscript.mapObj` or :class:`mapscript.layerObj`. Uses 
    :meth:`getProjection` and :meth:`setProjection` to retrieve projection 
    information.

    e.g.::

        MAP
            PROJECTION
                "proj=lcc"
                "lat_1=51.16666723333333"
                "lat_2=49.8333339"
                "lat_0=90"
                "lon_0=4.367486666666666"
                "x_0=150000.013"
                "y_0=5400088.438"
                "ellps=intl"
                "towgs84=-106.869,52.2978,-103.724,0.3366,-0.457,1.8422,-1.2747"
                "units=m"
                "no_defs"
            END
        END

    """

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        return self.decode(self.instance_mapscript.getProjection())

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
        self.instance_mapscript.setProjection(self.encode(value))



class Size(Property):
    """
    Class for setting and getting the map size in pixels. Uses 
    :meth:`getSize` and :meth:`setSize` on the :class:`mapscript.mapObj` for
    retrieval of values. The return/set value is a :func:`tuple` in the form of 
    (width, height).

    e.g.::

        MAP
            SIZE 1000 1000
        END

    """

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        return self.instance_mapscript.getSize()

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
        self.instance_mapscript.setSize(value[0], value[1])



class String(Property):
    """
    Class for mapping string values to and from JSON. Uses
    :ref:`method-property-decode` and :ref:`method-property-encode` to read
    the values from a mapfile correctly and transfer them between the JSON 
    encoding.
    """

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        # print type(self.decode(getattr(self.instance_mapscript, self.property_name)))
        return self.decode(self._getattr())

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
        if value is not None:
            value = self.encode(value)
        self._setattr(value)



class Text(Property):
    """
    Class for retrieving and setting the :attr:`text` of a :class:`classObj`.
    Uses :meth:`getTextString` and :meth:`setText` on the
    :class:`mapscript.classObj`.

    e.g.::

        CLASS
            TEXT "N"
        END

    """

    def __get__(self, instance, owner):
        Property.__get__(self, instance, owner)
        if instance is None:
            return self
        value = self.decode(self.instance_mapscript.getTextString())
        if value is not None:
            return value.replace('"', '')
        return value

    def __set__(self, instance, value):
        Property.__set__(self, instance, value)
        if value is not None:
            value = self.encode(value)
        self.instance_mapscript.setText(value)
