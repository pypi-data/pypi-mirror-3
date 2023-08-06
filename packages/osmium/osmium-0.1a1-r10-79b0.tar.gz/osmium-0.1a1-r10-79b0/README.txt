=================
Osmium for Python
=================

This is a Python port of the Osmium (http://wiki.openstreetmap.org/wiki/Osmium) library,
which provides a fast and flexible toolkit for working with Open Street Map data.

Currently there is only a small subset of the Osmium toolkit implemented. You
can read and write OSM files in different formats and process them through a
customized filter. See below for details.


Installation
============

Prerequisites
-------------

Osmium depends on the following C/C++ libraries.
Please make sure they are installed.

 * Osmium library (https://github.com/joto/osmium)
 * Boost (http://www.boost.org)
 * Expat (http://expat.sourceforge.net)
 * Google Protocol buffers (http://code.google.com/p/protobuf/)
 * xml2 (http://xmlsoft.org/)
 * zlib (http://www.zlib.net)

If you have a Debian based distribution, you can install the required packages by::

    $ sudo apt-get install libosmium-dev libboost-dev libexpat1-dev libprotobuf-dev protobuf-compiler zlib1g-dev libxml2-dev


Building
--------

If all libraries are installed in their default location, you can install directly from `PyPI`_
using `pip`_ or `setuptools`_ by running the respective command::

    $ pip install -U osmium

or::

    $ easy_install -U osmium

Otherwise you can download osmium and install the library directy from source::

    $ python setup.py install

In each case the installer will try to find the needed libraries and abort if something is missing.

.. _`PyPI`: http://pypi.python.org/
.. _`pip`: http://www.pip-installer.org/
.. _`setuptools`: http://pypi.python.org/pypi/setuptools

Manual configuration
--------------------

This package comes with a GNU autoconf ``configure`` script. You have to call it manually, if 
some libraries are in non-standard places. You can call it like::

    $ sh ./configure --with-osmium=/path/to/osmium/include --with-expat=/path/to/expat

before continuing like above::

    $ python setup.py install

The ``configure`` script accepts the following parameters

  * ``--with-osmium``: include directory of Osmium installation
  * ``--with-expat``: prefix of Expat installation

All other libraries register with ``pkg-config``. Please make sure it is installed. 
If it is in some non-standard location, you have to set the 
environment variable ``PKG_CONFIG``::
    
    $ PKG_CONFIG='/my/special/pkg-config' ./configure


Basic Usage
===========

You usually build a filtering chain by opening an ``osmium.OSMFile`` and read it through a
``osmium.handler.*`` class. To process all contents of a file through the 
`osmium.handler.Debug` handler, you can write
::

    import osmium

    infile = osmium.OSMFile(b'my_city.osm.pbf')
    handler = osmium.handler.Debug()
    infile.read(handler)

There are also handlers, which write the processed objects to a file. You can create such
a handler via the ``create_output_file`` method::

    import osmium
    
    infile = osmium.OSMFile(b'my_city.xml.gz')
    outfile = osmium.OSMFile(b'my_city.osm.pbf')
    
    handler = outfile.create_output_file()
    infile.read(handler) 

This little program converts the file ``my_city.xml.gz`` (expected in XML format) 
to ``my_city.osm.pbf`` (which is written in PBF Format).

.. note::

    Be careful with the ``create_output_file`` method. If the file already exists, it will
    be truncated silently.

You can also write your own handlers. To print out all cities, use::

    import osmium

    class CityPrinterHandler(osmium.handler.Base):
        
        def node(self, node):
            if node.tags.get('place')=='city':
                print(node.tags.get('name'))

    infile = osmium.OSMFile(b'my_country.osm.pbf')
    handler = CityPrinterHandler()

    infile.read(handler)

.. note::

    Please note, that until now the Python wrapper has a **read only** interface to
    nodes, ways and relations. This means, you can't change or add objects, but you
    can access all attributes and filter objects according to them.

.. vim: syntax=rst
