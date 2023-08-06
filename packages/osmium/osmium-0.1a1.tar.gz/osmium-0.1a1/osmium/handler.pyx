# cython: language_level=3
from cpython.ref cimport PyObject
from _callback_handler cimport CallbackHandler

from c_osmium.handler cimport Debug as c_Debug, Progress as c_Progress
from c_osmium.osm cimport NodePtr, castNodePtr, castWayPtr, castRelationPtr, Meta as c_Meta
from osmium.osm cimport _cache_node, _cache_taglist, _cache_way, _cache_waynodelist, _cache_relation, _cache_relationmemberlist


cdef public class Base[object osmhandler_struct, type osmhandler_type]:
    """base class for python implemented handlers
    """

    def __init__(self):
        self.cur_node = Node()

    cdef handle_infile(self, c_OSMFile *infile):
        """Creates the correct Handler class and calls the read method

        This is needed, because osmium doesn't support polymorphism with
        handlers.
        """
        cdef CallbackHandler *handler = new CallbackHandler(self)
        infile.read(handler[0])

    cpdef init(self, Meta curmeta):
        """init_callback(self, meta)
        default handler for init
        """
        pass

    cpdef before_nodes(self):
        pass

    cpdef node(self, Node curnode):
        """node_callback(self, curnode)
        default handler for nodes
        """
        pass

    cpdef after_nodes(self):
        pass

    cpdef before_ways(self):
        pass

    cpdef way(self, Way curway):
        """way_callback(self, curway)
        default handler for ways
        """
        pass

    cpdef after_ways(self):
        pass

    cpdef before_relations(self):
        pass

    cpdef relation(self, Relation currel):
        """relation_callback(self, curway)
        default handler for relations
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
