from c_osmium.osmfile cimport OSMFile as c_OSMFile
from c_osmium.osm cimport ConstNodePtr, ConstWayPtr, ConstRelationPtr
from c_osmium.handler cimport Debug as c_Debug, Progress as c_Progress
from osmium.osm cimport Meta, Node, Way, Relation

# hack for access to cpython exception objects
cdef extern from "pyerrors.h":
    ctypedef class __builtin__.Exception [object PyBaseExceptionObject]:
        pass

cdef public class StopReading(Exception) [object StopReading_struct, type StopReading_type]:
    """raise this exception to immediately stop reading the input file
    """
    pass

cdef public class Base[object osmhandler_struct, type osmhandler_type]:
    """base class for python implemented handlers
    """
    cdef Node cur_node
    cdef inline handle_infile(self, c_OSMFile *infile)

    cpdef init(self, Meta)
    cpdef before_nodes(self)
    cpdef node(self, Node)
    cpdef after_nodes(self)
    cpdef before_ways(self)
    cpdef way(self, Way)
    cpdef after_ways(self)
    cpdef before_relations(self)
    cpdef relation(self, Relation)
    cpdef after_relations(self)
    cpdef final(self)

cdef class Debug(Base):
    cdef c_Debug *c_handler

cdef class Progress(Base):
    cdef c_Progress *c_handler
    cpdef hide_cursor(self)
    cpdef show_cursor(self)

cdef class Tee(Base):
    cdef public Base handler1
    cdef public Base handler2

cdef class Forward(Base):
    cdef public Base handler
