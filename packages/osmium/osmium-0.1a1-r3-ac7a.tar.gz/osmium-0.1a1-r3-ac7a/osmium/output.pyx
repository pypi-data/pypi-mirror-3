from c_osmium.osm cimport castNodePtr, castWayPtr, castRelationPtr
from osmium.osm cimport Meta, Node, Way, Relation

cdef class Base(handler.Base):
    def __init__(self):
        raise TypeError("this type is not direct instantiable, use OSMFile instead")

    def __dealloc__(self):
        del self.c_output

    cdef handle_infile(self, c_OSMFile *infile):
        infile.read(self.c_output[0])

    cpdef init(self, Meta meta):
        self.c_output.init(meta.c_meta[0])

    cpdef node(self, Node node):
        self.c_output.node(castNodePtr(node.c_object[0]))

    cpdef way(self, Way way):
        self.c_output.way(castWayPtr(way.c_object[0]))

    cpdef relation(self, Relation rel):
        self.c_output.relation(castRelationPtr(rel.c_object[0]))

    cpdef before_nodes(self):
        self.c_output.before_nodes()
    cpdef after_nodes(self):
        self.c_output.after_nodes()
    cpdef before_ways(self):
        self.c_output.before_ways()
    cpdef after_ways(self):
        self.c_output.after_ways()
    cpdef before_relations(self):
        self.c_output.before_relations()
    cpdef after_relations(self):
        self.c_output.after_relations()
    cpdef final(self):
        self.c_output.final()
