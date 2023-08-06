from libcpp cimport bool
from libc.stdint cimport int32_t

cdef extern from "time.h":
    ctypedef int time_t

cdef extern from "osmium/osm/types.hpp":
    enum osm_object_type_t:
        UNKNOWN,
        NODE,
        WAY,
        RELATION,
        AREA_FROM_WAY,
        AREA_FROM_RELATION

    ctypedef int osm_object_id_t
    ctypedef unsigned int osm_version_t
    ctypedef int osm_changeset_id_t
    ctypedef int osm_user_id_t
    ctypedef unsigned int osm_sequence_id_t

cdef extern from "osmium/osm/tag.hpp" namespace "Osmium::OSM":
    cdef cppclass Tag:
        Tag(char*, char*)
        char *key()
        char *value()

cdef extern from "osmium/osm/tag_list.hpp" namespace "Osmium::OSM":
    ctypedef char * conststr "const char *"
    cdef cppclass TagListIterator "Osmium::OSM::TagList::iterator":
        Tag& operator*()
        Tag& deref "operator*"()
        TagListIterator inc "operator++"()
        TagListIterator operator++()
        TagListIterator operator--()
        bool operator==(TagListIterator)
        bool operator!=(TagListIterator)

    cdef cppclass TagList:
        int size()
        bool empty()
        void clear()
        Tag operator[](int)

        # this needs to be fixed if cython supports templates correctly
        #cppclass iterator:
        #   pass
        TagListIterator begin()
        TagListIterator end()

        void add(char*, char*) except+
        conststr get_tag_by_key(char *)
        conststr get_tag_key(unsigned int n) except+
        conststr get_tag_value(unsigned int n) except+


cdef extern from "osmium/osm/position.hpp" namespace "Osmium::OSM":
    cdef cppclass Position:
        Position()
        Position(int32_t,int32_t)
        Position(double,double)
        bool defined()
        int32_t x()
        int32_t y()
        double lon()
        double lat()
        Position& lon(double)
        Position& lat(double)
        
cdef extern from "osmium/osm/bounds.hpp" namespace "Osmium::OSM":
    cdef cppclass Bounds:
        Bounds& extend(Position&)
        bool defined()
        Position bl()
        Position tr()

cdef extern from "osmium/osm/meta.hpp" namespace "Osmium::OSM":
    cdef cppclass Meta:
        Bounds& bounds()
        bool has_multiple_object_versions()
        Meta& has_multiple_object_versions(bool)

cdef extern from "osmium/osm/object.hpp" namespace "Osmium::OSM":
    cdef cppclass Object:
        osm_object_id_t o_id "id" ()
        osm_version_t version()
        osm_changeset_id_t changeset()
        osm_user_id_t uid()
        time_t timestamp()
        time_t endtime()
        char * user()
        bool visible()
        TagList& tags()

cdef extern from "osmium/osm/node.hpp" namespace "Osmium::OSM":
    cdef cppclass Node(Object):
        Position position()
        Node& position(Position)

        void set_x(double)
        void set_y(double)

        double get_lon()
        double get_lat()


cdef extern from "osmium/osm/way_node.hpp" namespace "Osmium::OSM":
    cdef cppclass WayNode:
        WayNode()
        WayNode(osm_object_id_t)
        WayNode(osm_object_id_t, Position&)

        osm_object_id_t ref()
        Position& position()
        WayNode& position(Position&)
        bool has_position()

        double lon()
        double lat()

cdef extern from "osmium/osm/way_node_list.hpp" namespace "Osmium::OSM":
    cdef cppclass WayNodeListIterator "Osmium::OSM::WayNodeList::iterator":
        WayNode& operator*()
        WayNode& deref "operator*"()
        WayNodeListIterator inc "operator++"()
        WayNodeListIterator operator++()
        WayNodeListIterator operator--()
        bool operator==(WayNodeListIterator)
        bool operator!=(WayNodeListIterator)

    cdef cppclass WayNodeList:
        WayNodeList()
        WayNodeList(unsigned int)
        osm_sequence_id_t size()
        void clear()
        WayNodeListIterator begin()
        WayNodeListIterator end()
        WayNodeListIterator rbegin()
        WayNodeListIterator rend()

        WayNode& operator[](int)
        WayNode& front()
        WayNode& back()
        bool is_closed()
        bool has_position()
        WayNodeList& add(WayNode&)
        WayNodeList& add(osm_object_id_t)



cdef extern from "osmium/osm/way.hpp" namespace "Osmium::OSM":
    cdef cppclass Way(Object):
        Way()
        Way(int)
        Way(Way&)

        WayNodeList& nodes()
        
cdef extern from "osmium/osm/relation_member.hpp" namespace "Osmium::OSM":
    cdef cppclass RelationMember:
        osm_object_id_t ref()
        RelationMember& ref(osm_object_id_t)
        char typ "type"()
        char *type_name()
        RelationMember& typ "type"(char)

        char* role()
        RelationMember& role(char*)

cdef extern from "osmium/osm/relation_member_list.hpp" namespace "Osmium::OSM":
    cdef cppclass RelationMemberListIterator "Osmium::OSM::RelationMemberList::iterator":
        RelationMember& operator*()
        RelationMember& deref "operator*"()
        RelationMemberListIterator inc "operator++"()
        RelationMemberListIterator operator++()
        RelationMemberListIterator operator--()
        bool operator==(RelationMemberListIterator)
        bool operator!=(RelationMemberListIterator)

    cdef cppclass RelationMemberList:
        RelationMemberList()
        osm_sequence_id_t size()
        void clear()

        RelationMember& operator[](int)
        RelationMemberListIterator begin()
        RelationMemberListIterator end()
        void add_member(char, osm_object_id_t, char*)

cdef extern from "osmium/osm/relation.hpp" namespace "Osmium::OSM":
    cdef cppclass Relation(Object):
        Relation()
        Relation(Relation&)

        RelationMemberList& members()
        void add_member(char, osm_object_id_t, char*)
        RelationMember* get_member(osm_sequence_id_t)

cdef extern from "osmium/osm/area.hpp" namespace "Osmium::OSM":
    cdef enum innerouter_t:
        UNSET,
        INNER,
        OUTER

    cdef enum direction_t:
        NO_DIRECTION,
        CLOCKWISE,
        COUNTERCLOCKWISE

    cdef cppclass WayInfo:
        pass

    cdef cppclass RingInfo:
        pass

    cdef cppclass Area(Object):
        Area()

    cdef cppclass AreaFromWay(Area):
        AreaFromWay(Way*)
        WayNodeList& nodes()

    cdef cppclass AreaFromRelation(Area):
        AreaFromRelation(Relation*, bool, int, void*, bool)
        void add_member_way(Way*)
        bool is_complete()
        void handle_complete_multipolygon()

include "pointers.pxi"
