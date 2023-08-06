from libcpp cimport bool
from c_osmium.osm cimport Meta, ConstNodePtr, ConstWayPtr, ConstRelationPtr, Area

cdef extern from "osmium/handler.hpp" namespace "Osmium::Handler":
    cdef cppclass Base:
        Base()
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
        void area(Area*)
        void final()


cdef extern from "osmium/handler/debug.hpp" namespace "Osmium::Handler":

    cdef cppclass Debug(Base):
        Debug()
        Debug(bool)

cdef extern from "osmium/handler/progress.hpp" namespace "Osmium::Handler":

    cdef cppclass Progress(Base):
        Progress()
        Progress(int)
        void hide_cursor()
        void show_cursor()
