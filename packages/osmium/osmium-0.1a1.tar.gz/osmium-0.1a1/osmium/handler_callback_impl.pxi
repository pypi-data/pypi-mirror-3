# vim: filetype=pyrex

# Helper functions, call the appropriate methods of the associated osmhandler
cdef public inline int c_init_callback(Base handler, c_Meta &curmeta) except -1:
    cdef Meta pymeta = Meta()
    pymeta.set_from_c(curmeta)
    handler.init(pymeta)

cdef public inline int c_before_nodes_callback(Base handler) except -1:
    handler.before_nodes()
cdef public inline int c_after_nodes_callback(Base handler) except -1:
    handler.after_nodes()
cdef public inline int c_before_ways_callback(Base handler) except -1:
    handler.before_ways()
cdef public inline int c_after_ways_callback(Base handler) except -1:
    handler.after_ways()
cdef public inline int c_before_relations_callback(Base handler) except -1:
    handler.before_relations()
cdef public inline int c_after_relations_callback(Base handler) except -1:
    handler.after_relations()
cdef public inline int c_final_callback(Base handler) except -1:
    handler.final()

cdef public inline int c_node_callback(Base handler, ConstNodePtr &node) except -1:
    global _cache_node, _cache_taglist

    _cache_node.c_object[0] = node
    handler.node(_cache_node)

    if (<PyObject*>_cache_node).ob_refcnt == 1:
        _cache_node.c_object.reset()
    else:
        _cache_node = Node()

    if (<PyObject*>_cache_taglist).ob_refcnt == 1:
        _cache_taglist.c_object.reset()

cdef public inline int c_way_callback(Base handler, ConstWayPtr &way) except -1:
    global _cache_way, _cache_taglist, _cache_waynodelist

    _cache_way.c_object[0] = way
    handler.way(_cache_way)

    if (<PyObject*>_cache_way).ob_refcnt == 1:
        _cache_way.c_object.reset()
    else:
        _cache_way = Way()

    if (<PyObject*>_cache_taglist).ob_refcnt == 1:
        _cache_taglist.c_object.reset()

    if (<PyObject*>_cache_waynodelist).ob_refcnt == 1:
        _cache_waynodelist.c_way.reset()

cdef public inline int c_relation_callback(Base handler, ConstRelationPtr &rel) except -1:
    global _cache_relation, _cache_taglist, _cache_relationmemberlist

    _cache_relation.c_object[0] = rel
    handler.relation(_cache_relation)

    if (<PyObject*>_cache_relation).ob_refcnt == 1:
        _cache_relation.c_object.reset()
    else:
        _cache_relation = Relation()

    if (<PyObject*>_cache_taglist).ob_refcnt == 1:
        _cache_taglist.c_object.reset()

    if (<PyObject*>_cache_relationmemberlist).ob_refcnt == 1:
        _cache_relationmemberlist.c_relation.reset()
