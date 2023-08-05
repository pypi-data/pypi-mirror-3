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

from __future__ import with_statement
from codecs import open
from distutils.core import setup
import msjson


with open('README.rst', encoding='utf-8') as info:
    long_description = info.read()

setup(
    name='msjson',
    version=str(msjson.__version__),
    description='Converting UMN Mapserver mapscript objects from and to json',
    long_description=long_description,
    author=str(msjson.__author__),
    author_email='frank.broniewski@gmail.com',
    url='https://bitbucket.org/frankbroniewski/msjson',
    packages=['msjson'],
    requires=['mapscript'],
    license='GNU Lesser General Public License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Utilities'
    ]
)
