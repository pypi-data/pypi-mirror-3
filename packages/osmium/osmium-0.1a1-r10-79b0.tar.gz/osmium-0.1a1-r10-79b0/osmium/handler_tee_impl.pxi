# vim: filetype=pyrex

cdef class Tee(Base):
    u"""
    The Tee handler passes all events on to two other handlers.
    """

    def __init__(self, handler1, handler2):
        u"""__init__(self, handler1, handler2)
        Pass calls to both **handler1** and **handler2**.
        """
        self.handler1 = handler1
        self.handler2 = handler2

    cpdef init(self, Meta meta):
        self.handler1.init(meta)
        self.handler2.init(meta)

    cpdef node(self, Node node):
        self.handler1.node(node)
        self.handler2.node(node)

    cpdef way(self, Way way):
        self.handler1.way(way)
        self.handler2.way(way)

    cpdef relation(self, Relation rel):
        self.handler1.relation(rel)
        self.handler2.relation(rel)

    cpdef before_nodes(self):
        self.handler1.before_nodes()
        self.handler2.before_nodes()
    cpdef after_nodes(self):
        self.handler1.after_nodes()
        self.handler2.after_nodes()
    cpdef before_ways(self):
        self.handler1.before_ways()
        self.handler2.before_ways()
    cpdef after_ways(self):
        self.handler1.after_ways()
        self.handler2.after_ways()
    cpdef before_relations(self):
        self.handler1.before_relations()
        self.handler2.before_relations()
    cpdef after_relations(self):
        self.handler1.after_relations()
        self.handler2.after_relations()
    cpdef final(self):
        self.handler1.final()
        self.handler2.final()
