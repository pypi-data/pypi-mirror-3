# vim: filetype=pyrex

cdef class Debug(Base):
    u"""Print debugging output on each callback

    This class calls the Osmium debug handler and uses its hard coded 
    standard output. The output may not appear where you expect it.
    """

    def __cinit__(self):
        self.c_handler = new c_Debug()

    def __dealloc__(self):
        del self.c_handler

    def __init__(self):
        pass

    cdef handle_infile(self, c_OSMFile *infile):
        infile.read(self.c_handler[0])

    cpdef init(self, Meta meta):
        self.c_handler.init(meta.c_meta[0])

    cpdef node(self, Node curnode):
        self.c_handler.node(castNodePtr(curnode.c_object[0]))

    cpdef way(self, Way way):
        self.c_handler.way(castWayPtr(way.c_object[0]))

    cpdef relation(self, Relation rel):
        self.c_handler.relation(castRelationPtr(rel.c_object[0]))


    cpdef before_nodes(self):
        self.c_handler.before_nodes()
    cpdef after_nodes(self):
        self.c_handler.after_nodes()
    cpdef before_ways(self):
        self.c_handler.before_ways()
    cpdef after_ways(self):
        self.c_handler.after_ways()
    cpdef before_relations(self):
        self.c_handler.before_relations()
    cpdef after_relations(self):
        self.c_handler.after_relations()
    cpdef final(self):
        self.c_handler.final()
