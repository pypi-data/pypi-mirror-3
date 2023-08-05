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
    MsJSON Mapfile serialiser
    =========================

    A package for converting UMN Mapserver mapscript objects to and
    from JSON for Python 2.x.

    `Mapscript: <http://mapserver.org/mapscript/>`_

    `JSON: <http://www.json.org/>`_

    `Package index <http://pypi.python.org/pypi/msjson/>`_

    `Bitbucket project page <https://bitbucket.org/frankbroniewski/msjson>`_


    .. _installation:

    Installation
    ------------

    From pypi::

        easy_install -U msjson

    or from a downloaded archive (Bitbucket or pypi)::

        python setup.py install
    

    .. _usage:

    Usage
    -----

    The usage is simple::

        # coding: utf-8

        import mapscript
        import msjson

        msobj = mapscript.mapObj('/path/to/mapfile.map')
        m = Map(mapscript_=msobj, mapfile_encoding='cp1252')
        print m.to_json()

    or to convert an object from json.load(s)::

        json_object = {
            'name' : 'Foo',
            'imagecolor' : {
                'red': 255, 'green': 255, 'blue': 255
            }
        }
        m = Map()
        m.mapfile_encoding = 'cp1252'
        m.from_json(json_object)
        m.mapscript.save('/path/to/mapfile.map')

    You can also set the properties directly::

        m = Map()
        m.name = 'Foo'
        m.imagecolor = {'red': 255, 'green': 255, 'blue': 255}

    Just make sure that everything after the equal sign is the jsonable
    representation of the value. For examples of the JSON representation
    of an object see their documentation.

    .. note::
        Only properties necessary for the configuration are serialised.
        Mapscript properties like numlayers are skipped. But you can easily
        add them to your configuration.

    The serialisation of almost any mapscript.xyzObj is supported, just pass
    it as an argument to the appropriate msjson class object. Right now the
    package lacks support for 
    `mapscript.fontSetObj <http://mapserver.org/mapscript/mapscript.html#fontsetobj>`_
    and the outputformat list for the 
    `mapscript.mapObj <http://mapserver.org/mapscript/mapscript.html#mapobj>`_ 
    [1]_. The currently selected outputformat can be 
    exported though through the use of :class:`msjson.OutputFormat`.

    .. note::
        
        The JSON of a serialised map file can contain more attributes than 
        defined in the map file. This is due to the nature of mapscript
        where most properties have default values defined. Some properties,
        like colors have a value for beeing "not set". These values are also
        read and transformed into JSON if being configured on the
        corresponding msjson object.

        So if your map file holds no background image color configuration
        value, but the backgroundcolor property is defined on the
        :ref:`class-map` it is read from the :class:`mapscript.mapObj`
        and transformed into JSON.

        This behavior may change in the future!
    
    The logic of the package is based on the `descriptor pattern 
    <http://docs.python.org/reference/datamodel.html?#implementing-descriptors>`_ 
    in Python and the style of the configuration is borrowed from database ORM 
    libraries like `SQLAlchemy <http://www.sqlalchemy.org/>`_.


    Mapscript compatibility between versions
    ----------------------------------------

    It may happen that properties on mapscript objects are existant in one
    version but not in another. Mapscript on Debian Squeeze 6 is of version
    5.6.6, Mapscript on Ubunut 8.04 is of Version 6.0.0 (from the UbuntuGIS
    repository). The Debian version features a :attr:`autoangle` property on
    the :class:`labelObj` while the Ubuntu version does not.

    Debian 6 Squeeze::

        >>> import mapscript
        >>> hasattr(mapscript.labelObj(), 'autoangle')
        True

    Ubuntu 8.04 (UbuntuGIS)::
        
        >>> import mapscript
        >>> hasattr(mapscript.labelObj(), 'autoangle')
        False

    This may be true for more properties than :attr:`autoangle`. To circumvent
    problems with properties that do not exist on certain mapscript versions
    the logic of MsJSON deals flexible with non-existant properties. When you 
    call :meth:`to_json` and a non-existant property is encounterd on the 
    mapscript object a value of None is bound to the defined property name.
    Equally when trying to set a value on a non-existant property the action 
    is skipped if the property doesn't exist. In each case a DeprecationWarning
    is issued. Depending on your Python version the output of the warning may
    be suppressed.


    .. _own-jsonifiers:

    Own Jsonifiers
    --------------

    You can create your own Classes for JSON serialisation, there is no need
    to stick to the predefined classes from the package. Just define your own
    handlers and you are ready to go::

        # coding: utf-8
        import mapscript
        import msjson
        from msjson.base import Base

        class MyMap(Base):
            base = mapscript.mapObj

            # json attribute = mapscript attribute
            a_name = msjson.String('name')
            a_color = msjson.Color('imagecolor')
            numlayers = msjson.Integer('numlayers')

        m = MyMap()
        m.to_json()

    Each class derived from :ref:`class-base` must have a class property 
    :attr:`base` wich holds a reference to the corresponding mapscript object.
    Everything else can be configured as needed.


    Using classes below Map
    -----------------------

    For every mapscript.xyzObj exists a represention class in the package
    wich deals with the conversion from and to JSON. There are different kinds
    of conversion handlers which deal with different aspects of the mapscript
    behavior in retrieving and setting values. There are :ref:`types`,
    :ref:`datatypes`, :ref:`base-classes` and :ref:`classes`.

    .. _types:

    Types
    ^^^^^

    There are classes, so called types, for the most basic data representations
    in mapscript. These are:

    - :ref:`class-collection`
        
    - :ref:`class-expression`

    - :ref:`class-float`

    - :ref:`class-imagetype`

    - :ref:`class-integer`

    - :ref:`class-projection`

    - :ref:`class-property`

    - :ref:`class-size`

    - :ref:`class-string`

    - :ref:`class-text`

    Since these are mostly values they do not have a direct jsonable 
    representation but return values directly with the exception of 
    :class:`msjson.Collection` and :class:`msjson.Size` which return lists.


    .. _datatypes:

    Datatypes
    ^^^^^^^^^

    Datatypes represent `mapscripts variables 
    <http://mapserver.org/mapscript/variables.html>`_ and map directly between
    Python data types and mapscript variables. Like :ref:`module-types`, these
    also do not have a jsonable representation and return values directly. 
    There are the following classes:

    - :ref:`class-boolean`

    - :ref:`class-connection`

    - :ref:`class-imagemode`

    - :ref:`class-layertype`

    - :ref:`class-position`

    - :ref:`class-status`

    - :ref:`class-unit`


    .. _base-classes:
    
    Base classes
    ^^^^^^^^^^^^

    Base classes represent a mapscript.xyzObj and may have one or more 
    :ref:`types`, :ref:`datatypes` or other :ref:`base-classes` as properties.

    Base classes are:

    - :ref:`class-fontset` (currently not fully functional)

    - :ref:`class-label`

    - :ref:`class-legend`

    - :ref:`class-outputformat`

    - :ref:`class-scalebar`

    - :ref:`class-style`

    - :ref:`class-web`


    .. _classes:

    Classes
    ^^^^^^^

    Classes are the top level representations of mapscript objects. Classes
    include:

    - :ref:`class-class`

    - :ref:`class-layer`

    - :ref:`class-map`

    Each class has a collection object which wraps around the number of child 
    elements of each class, i.e. the layers of the mapscript.mapObj object, 
    the classes of the mapscript.layerObj object and the styles of the 
    :class:`mapscript.classObj` object. There is no direct iteration over child
    elements of an object in mapscript so the :ref:`class-collection` class is
    used for retrieving, removing and inserting child elements.
"""


from msjson.types import Collection, Expression, Float, ImageType, Integer,\
                         Projection, Property, Size, String, Text
from msjson.datatypes import Boolean, LayerType, Status, Unit
from msjson.base import Color, HashTable, Rect
from msjson.baseclasses import FontSet, Label, Legend, OutputFormat,\
                               ScaleBar, Style, Web
from msjson.classes import Class, Map, Layer


__author__ = 'Frank Broniewski, Metrico s.à r.l'
__date__ = '2011-07-28'
__version__ = '0.2.2'
__version_info__ = tuple(map(int, __version__.split('.')))
