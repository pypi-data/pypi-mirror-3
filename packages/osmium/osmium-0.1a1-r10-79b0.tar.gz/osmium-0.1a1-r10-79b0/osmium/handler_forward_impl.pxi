# vim: filetype=pyrex

cdef class Forward(Base):
    u"""
    This handler forwards all calls to another handler.
    Use this as a base for your handler instead of Base() if you want calls
    forwarded by default.
    """

    def __init__(self, handler):
        u"""__init__(self, handler)
        Use **handler** as destination.
        """
        self.handler = handler

    cpdef init(self, Meta meta):
        self.handler.init(meta)

    cpdef node(self, Node node):
        self.handler.node(node)

    cpdef way(self, Way way):
        self.handler.way(way)

    cpdef relation(self, Relation rel):
        self.handler.relation(rel)

    cpdef before_nodes(self):
        self.handler.before_nodes()
    cpdef after_nodes(self):
        self.handler.after_nodes()
    cpdef before_ways(self):
        self.handler.before_ways()
    cpdef after_ways(self):
        self.handler.after_ways()
    cpdef before_relations(self):
        self.handler.before_relations()
    cpdef after_relations(self):
        self.handler.after_relations()
    cpdef final(self):
        self.handler.final()
