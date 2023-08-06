u"""
Basic OSMFile Handlers
======================

Handlers process OSM data. This module contains the Base handler
and some building blocks for other handlers.

Base:     Handler base class
Forward:  Forwards each call to another handler
Debug:    Prints debugging output on each callback
Progress: Prints progress information
Tee:      Forwards each call to two other handlers

All handlers in this package are implemented in C++ or at least Cython
to ensure fast operation.
"""

from cpython.ref cimport PyObject
from _callback_handler cimport CallbackHandler

from c_osmium.handler cimport Debug as c_Debug, Progress as c_Progress
from c_osmium.osm cimport NodePtr, castNodePtr, castWayPtr, castRelationPtr, Meta as c_Meta
from osmium.osm cimport _cache_node, _cache_taglist, _cache_way, _cache_waynodelist, _cache_relation, _cache_relationmemberlist


cdef public class Base[object osmhandler_struct, type osmhandler_type]:
    u"""Base class for python implemented handlers
    """

    cdef handle_infile(self, c_OSMFile *infile):
        u"""Create the correct Handler class and call the read method of infile on it.

        This is needed, because osmium doesn't support polymorphism with
        handlers.
        """
        cdef CallbackHandler *handler = new CallbackHandler(self)
        infile.read(handler[0])

    cpdef init(self, Meta curmeta):
        u"""init_callback(self, meta)
        Begin handling OSM data.
        """
        pass

    cpdef before_nodes(self):
        u"""before_nodes(self)
        """
        pass

    cpdef node(self, Node node):
        u"""node_callback(self, node)
        called for each node
        """
        pass

    cpdef after_nodes(self):
        u"""after_nodes(self)
        """
        pass

    cpdef before_ways(self):
        u"""before_ways(self)
        """
        pass

    cpdef way(self, Way way):
        """way_callback(self, way)
        called for each way
        """
        pass

    cpdef after_ways(self):
        u"""after_ways(self)
        """
        pass

    cpdef before_relations(self):
        u"""before_relations(self)
        """
        pass

    cpdef relation(self, Relation relation):
        """relation_callback(self, relation)
        called for each relation
        """
        pass

    cpdef after_relations(self):
        pass

    cpdef final(self):
        pass

include "handler_debug_impl.pxi"
include "handler_progress_impl.pxi"

include "handler_tee_impl.pxi"
include "handler_forward_impl.pxi"

include "handler_callback_impl.pxi"
