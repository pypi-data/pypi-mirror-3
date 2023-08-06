from c_osmium.osm cimport TagList as c_TagList, ObjectPtr, WayPtr, RelationPtr, Meta as c_Meta, Bounds as c_Bounds

cdef class TagList:
    cdef ObjectPtr *c_object

cdef class WayNodeList:
    cdef WayPtr *c_way

cdef class RelationMemberList:
    cdef RelationPtr *c_relation

cdef class Object:
    """Base class for OSM objects
    
    Represents a OSM::Object
    """
    cdef ObjectPtr *c_object

cdef class Node(Object):
    """OSM Node object

    Python access to a node.
    """
    pass

cdef class Way(Object):
    """OSM Way object
    """
    pass

cdef class Relation(Object):
    """OSM Relation object
    """
    pass

cdef class Bounds:
    cdef c_Bounds* c_bounds


cdef class Meta:
    """Meta information from the header of an OSM file.
    """
    cdef c_Meta* c_meta
    cdef readonly Bounds bounds
    cdef set_from_c(self, c_Meta &newval)

# Cache objects
cdef Node _cache_node
cdef Way _cache_way
cdef Relation _cache_relation
cdef TagList _cache_taglist
cdef WayNodeList _cache_waynodelist
cdef RelationMemberList _cache_relationmemberlist
