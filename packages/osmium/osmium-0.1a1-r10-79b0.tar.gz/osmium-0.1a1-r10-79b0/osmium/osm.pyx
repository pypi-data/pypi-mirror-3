u"""
OSM
===

Contains basic classes for OSM objects:

Meta:     metainformation of OSM file
Object:   common ancestor for OSM objects
Node:     OSM node
Way:      OSM way
Relation: OSM relation
"""

from c_osmium.osm cimport ConstObjectPtr, ConstRelationPtr, Object as c_Object, Node as c_Node, TagList as c_TagList, TagListIterator as c_TagListIterator, Way as c_Way, Relation as c_Relation, WayNodeList as c_WayNodeList, WayNodeListIterator as c_WayNodeListIterator, RelationMemberList as c_RelationMemberList, RelationMemberListIterator as c_RelationMemberListIterator, castWayPtr, castRelationPtr
from cpython.ref cimport PyObject


# Workaround definitions for const pointers
cdef extern from *:
    ctypedef c_Object * ObjectCPtr "Osmium::OSM::Object const*"
    ctypedef c_Node * NodeCPtr "Osmium::OSM::Node const*"
    ctypedef c_Way * WayCPtr "Osmium::OSM::Way const*"
    ctypedef c_Relation * RelCPtr "Osmium::OSM::Relation const*"
    ctypedef c_TagList * TagListCPtr "Osmium::OSM::TagList const*"


cdef inline ObjectCPtr _getOsmObject(ConstObjectPtr *ptr) except NULL:
    """Get object pointer from smart pointer and ensure it is not null
    """
    cdef ObjectCPtr retval = ptr.get()
    assert retval is not NULL, u"invalid ObjectPtr"
    return retval

cdef inline c_TagList* _getOsmTagList(ConstObjectPtr *ptr) except NULL:
    """Get TagList from object pointer
    """
    cdef ObjectCPtr obj = ptr.get()
    assert obj is not NULL, u"invalid ObjectPtr"
    return <c_TagList*>(&obj.tags())

cdef inline NodeCPtr _getOsmNode(ConstObjectPtr *ptr) except NULL:
    """Get object pointer from smart pointer and cast to node pointer
    """
    cdef NodeCPtr retval = <NodeCPtr>ptr.get()
    assert retval is not NULL, u"invalid ObjectPtr"
    return retval

cdef inline WayCPtr _getOsmWay(ConstObjectPtr *ptr) except NULL:
    """Get object pointer from smart pointer and cast to way pointer
    """
    cdef WayCPtr retval = <WayCPtr>ptr.get()
    assert retval is not NULL, u"invalid ObjectPtr"
    return retval

cdef inline c_WayNodeList* _getOsmWayNodeList(WayPtr *ptr) except NULL:
    """Get TagList from object pointer
    """
    cdef WayCPtr obj = <WayCPtr>ptr.get()
    assert obj is not NULL, u"invalid ObjectPtr"
    return <c_WayNodeList*>(&obj.nodes())

cdef inline c_RelationMemberList* _getOsmRelMemList(ConstRelationPtr *ptr) except NULL:
    """Get object pointer from smart pointer and cast to relation pointer
    """
    cdef RelCPtr obj = <RelCPtr>ptr.get()
    assert obj is not NULL, u"invalid ObjectPtr"
    return <c_RelationMemberList*>(&obj.members())


cdef class Object:
    """Base class for OSM objects
    
    Represents a OSM::Object
    """
    def __cinit__(self):
        self.c_object = new ObjectPtr()

    def __dealloc__(self):
        del self.c_object

    property id_:
        def __get__(self):
            return _getOsmObject(self.c_object).o_id()
    property version:
        def __get__(self):
            return _getOsmObject(self.c_object).version()
    property changeset:
        def __get__(self):
            return _getOsmObject(self.c_object).changeset()
    property uid:
        def __get__(self):
            return _getOsmObject(self.c_object).uid()
    property timestamp:
        def __get__(self):
            return _getOsmObject(self.c_object).timestamp()
    property endtime:
        def __get__(self):
            return _getOsmObject(self.c_object).endtime()
    property user:
        def __get__(self):
            return (<char*>_getOsmObject(self.c_object).user()).decode('utf-8')
    property visible:
        def __get__(self):
            return _getOsmObject(self.c_object).visible()
    property tags:
        def __get__(self):
            global _cache_taglist
            if (<PyObject*>_cache_taglist).ob_refcnt > 1:
                _cache_taglist = TagList()

            _cache_taglist.c_object[0] = self.c_object[0]
            return _cache_taglist

    
cdef class Node(Object):
    """OSM Node object

    Python access to a node.
    """

    property lon:
        def __get__(self):
            return _getOsmNode(self.c_object).get_lon()
    property lat:
        def __get__(self):
            return _getOsmNode(self.c_object).get_lat()


cdef class WayNodeList:
    """List interface to the NodeList property
    """
    def __cinit__(self):
        self.c_way = new WayPtr()
    def __dealloc__(self):
        del self.c_way

    def __len__(self):
        return _getOsmWayNodeList(self.c_way).size()

    def __str__(self):
        cdef c_WayNodeListIterator it
        cdef bint first = True
        cdef c_WayNodeList* c_waynodelist = _getOsmWayNodeList(self.c_way)

        res = "["
        it = c_waynodelist.begin()
        while it != c_waynodelist.end():
            if first:
                first = False
            else:
                res += ', '

            res += str(it.deref().ref())
            it.inc()

        res += ']'
        return res

    def __getitem__(self, unsigned int num):
        cdef c_WayNodeList* tmp = _getOsmWayNodeList(self.c_way)
        if num >= tmp.size():
            raise IndexError('list index out of range')

        return tmp[0][num].ref()

    def __iter__(self):
        cdef c_WayNodeListIterator* it = new c_WayNodeListIterator()
        cdef c_WayNodeList* c_waynodelist = _getOsmWayNodeList(self.c_way)

        it[0] = c_waynodelist.begin()
        while it[0] != c_waynodelist.end():
            yield it.deref().ref()
            it.inc()


cdef class Way(Object):
    """OSM Way object
    """

    property nodes:
        def __get__(self):
            global _cache_waynodelist
            if (<PyObject*>_cache_waynodelist).ob_refcnt > 1:
                _cache_taglist = WayNodeList()

            _cache_waynodelist.c_way[0] = castWayPtr(self.c_object[0])
            return _cache_waynodelist

cdef class RelationMemberList:
    """List interface to the relation members
    """
    def __cinit__(self):
        self.c_relation = new RelationPtr()

    def __dealloc__(self):
        del self.c_relation

    def __len__(self):
        return _getOsmRelMemList(self.c_relation).size()

    def __getitem__(self, unsigned int num):
        cdef c_RelationMemberList* c_ml = _getOsmRelMemList(self.c_relation)
        if num > c_ml.size():
            raise IndexError('list index out of range')
        return (c_ml[0][num].ref(), chr(c_ml[0][num].typ()), (<char*>c_ml[0][num].role()).decode('utf-8'))

    def __str__(self):
        cdef c_RelationMemberListIterator it
        cdef bint first = True
        cdef c_RelationMemberList* c_ml = _getOsmRelMemList(self.c_relation)

        res = "["
        it = c_ml.begin()
        while it != c_ml.end():
            if first:
                first = False
            else:
                res += ', '

            res += '('+str(it.deref().ref()) + ', '
            res += repr(chr(it.deref().typ()))+', '
            res += repr((<char*>it.deref().role()).decode('utf-8'))+')'
            it.inc()

        res += ']'
        return res

    def __iter__(self):
        cdef c_RelationMemberListIterator *it = new c_RelationMemberListIterator()
        cdef c_RelationMemberList* c_ml = _getOsmRelMemList(self.c_relation)

        it[0] = c_ml.begin()
        while it[0] != c_ml.end():
            yield (it.deref().ref(), chr(it.deref().typ()), (<char*>it.deref().role()).decode('utf-8'))
            it.inc()


cdef class Relation(Object):
    """OSM Relation object
    """
    property members:
        def __get__(self):
            global _cache_relationmemberlist
            if (<PyObject*>_cache_relationmemberlist).ob_refcnt > 1:
                _cache_relationmemberlist = RelationMemberList()

            _cache_relationmemberlist.c_relation[0] = castRelationPtr(self.c_object[0])
            return _cache_relationmemberlist

cdef class TagList:
    """List interface to the TagList property
    """
    def __cinit__(self):
        self.c_object = new ObjectPtr()

    def __dealloc__(self):
        del self.c_object

    def __len__(self):
        return _getOsmTagList(self.c_object).size()

    def __str__(self):
        cdef c_TagListIterator it
        cdef bint first=True
        cdef c_TagList* c_taglist = _getOsmTagList(self.c_object)

        res = "{"
        it = c_taglist.begin()
        while it!=c_taglist.end():
            if first:
                first = False
            else:
                res += ', '

            res += "'"+(<char*>it.deref().key()).decode('utf-8')+"': "
            res += "'"+(<char*>it.deref().value()).decode('utf-8')+"'"
            it.inc()
        res += '}'
        return res

    def __getitem__(self, key):
        cdef bytes key_b = key.encode('utf-8')
        cdef char * res = <char*>_getOsmTagList(self.c_object).get_tag_by_key(key_b)
        if res is NULL:
            raise KeyError(key)

        return res.decode('utf-8')

    def keys(self):
        cdef c_TagList* c_taglist = _getOsmTagList(self.c_object)
        cdef c_TagListIterator *it = new c_TagListIterator()

        it = new c_TagListIterator()
        it[0] = c_taglist.begin()
        while it[0] != c_taglist.end():
            yield (<char*>it.deref().key()).decode('utf-8')
            it.inc()

    def __iter__(self):
        return self.keys()

    def values(self):
        cdef c_TagList* c_taglist = _getOsmTagList(self.c_object)
        cdef c_TagListIterator *it = new c_TagListIterator()

        it[0] = c_taglist.begin()
        while it[0] != c_taglist.end():
            yield (<char*>it.deref().value()).decode('utf-8')
            it.inc()

    def items(self):
        cdef c_TagList* c_taglist = _getOsmTagList(self.c_object)
        cdef c_TagListIterator *it = new c_TagListIterator()

        it[0] = c_taglist.begin()
        while it[0]!=c_taglist.end():
            yield (
                    (<char*>it.deref().key()).decode('utf-8'),
                    (<char*>it.deref().value()).decode('utf-8')
                )
            it.inc()


cdef class Bounds:
    """Bounding box information from the header of an OSM file.
    """
    def __cinit__(self):
        self.c_bounds = new c_Bounds()

    def __dealloc__(self):
        del self.c_bounds

    property defined:
        def __get__(self):
            return self.c_bounds.defined()

    property bottom:
        def __get__(self):
            return self.c_bounds.bl().lat()

    property left:
        def __get__(self):
            return self.c_bounds.bl().lon()

    property top:
        def __get__(self):
            return self.c_bounds.tr().lat()

    property right:
        def __get__(self):
            return self.c_bounds.tr().lon()

    def __str__(self):
        res = "(("
        res += str(self.c_bounds.bl().lon())
        res += ", "
        res += str(self.c_bounds.bl().lat())
        res += "), ("
        res += str(self.c_bounds.tr().lon())
        res += ", "
        res += str(self.c_bounds.tr().lat())
        res += "))"
        return res

cdef class Meta:
    """Meta information from the header of an OSM file.
    """
    def __cinit__(self):
        self.c_meta = new c_Meta()

    def __init__(self):
        self.bounds = Bounds()

    def __dealloc__(self):
        del self.c_meta

    cdef set_from_c(self, c_Meta &newval):
        self.c_meta[0] = newval
        self.bounds.c_bounds[0] = self.c_meta.bounds()

    property has_multiple_object_versions:
        def __get__(self):
            return self.c_meta.has_multiple_object_versions()

    def __str__(self):
        res = "{multiple_versions: "
        res += str(self.c_meta.has_multiple_object_versions())
        res += ", bounds: "
        if self.bounds.defined:
            res += str(self.bounds)
        else:
            res += 'not set'
        res += "}"
        return res

_cache_node = Node()
_cache_way = Way()
_cache_taglist = TagList()
_cache_waynodelist = WayNodeList()
_cache_relation = Relation()
_cache_relationmemberlist = RelationMemberList()
