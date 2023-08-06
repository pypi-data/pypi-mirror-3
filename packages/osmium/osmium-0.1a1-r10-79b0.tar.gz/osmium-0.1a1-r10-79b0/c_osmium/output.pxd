
from c_osmium.osmfile cimport OSMFile
from c_osmium.osm cimport ConstNodePtr, ConstWayPtr, ConstRelationPtr, Meta

cdef extern from "osmium/output.hpp" namespace "Osmium::Output":
    cdef cppclass Base:
        Base(OSMFile&)
        void init(Meta)
        void before_nodes()
        void node(ConstNodePtr)
        void after_nodes()
        void before_ways()
        void way(ConstWayPtr)
        void after_ways()
        void before_relations()
        void relation(ConstRelationPtr)
        void after_relations()
        void final()
