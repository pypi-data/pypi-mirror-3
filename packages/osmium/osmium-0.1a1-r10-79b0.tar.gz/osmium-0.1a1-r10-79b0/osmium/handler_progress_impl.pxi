# vim: filetype=pyrex

cdef class Progress(Base):
    u"""
    Simple handler that shows progress on terminal by counting
    the number of nodes, ways, and relations already read and
    printing those counts to stdout.
     
    If stdout is not a terminal, nothing is printed.
     
    Note that this handler will hide the cursor. If the program
    is terminated before the final handler is called, it will not
    be re-activated. Call show_cursor() from an interrupt
    handler or similar, to do this properly.

    This class calls the Osmium debug handler and uses its hard coded
    standard output. The progress information may not appear where
    you expect it.
    """
 

    def __cinit__(self, int step=1000):
        self.c_handler = new c_Progress(step)

    def __dealloc__(self):
        del self.c_handler

    def __init__(self, int step=1000):
        pass

    cdef handle_infile(self, c_OSMFile *infile):
        infile.read(self.c_handler[0])

    cpdef hide_cursor(self):
        self.c_handler.hide_cursor()

    cpdef show_cursor(self):
        self.c_handler.show_cursor()

    cpdef init(self, Meta meta):
        self.c_handler.init(meta.c_meta[0])

    cpdef node(self, Node curnode):
        self.c_handler.node(castNodePtr(curnode.c_object[0]))

    cpdef way(self, Way way):
        self.c_handler.way(castWayPtr(way.c_object[0]))

    cpdef relation(self, Relation rel):
        self.c_handler.relation(castRelationPtr(rel.c_object[0]))

    cpdef final(self):
        self.c_handler.final()
