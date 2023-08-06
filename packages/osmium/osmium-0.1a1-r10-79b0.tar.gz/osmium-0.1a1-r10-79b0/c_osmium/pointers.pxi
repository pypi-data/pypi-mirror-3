# define all pointer classes here
# vim:filetype=pyrex
#
# This hack is needed until we have good template support in Cython

cdef extern from *:
    cdef cppclass ObjectPtr "shared_ptr<const Osmium::OSM::Object>":
        Object * get()
        void reset()

    cdef cppclass NodePtr "shared_ptr<const Osmium::OSM::Node>"(ObjectPtr):
        pass

    cdef cppclass WayPtr "shared_ptr<const Osmium::OSM::Way>"(ObjectPtr):
        pass

    cdef cppclass RelationPtr "shared_ptr<const Osmium::OSM::Relation>"(ObjectPtr):
        pass

    cdef cppclass AreaPtr "shared_ptr<const Osmium::OSM::Area>"(ObjectPtr):
        pass

    ctypedef ObjectPtr ConstObjectPtr "const shared_ptr<const Osmium::OSM::Object>"
    ctypedef NodePtr ConstNodePtr "const shared_ptr<const Osmium::OSM::Node>"
    ctypedef WayPtr ConstWayPtr "const shared_ptr<const Osmium::OSM::Way>"
    ctypedef RelationPtr ConstRelationPtr "const shared_ptr<const Osmium::OSM::Relation>"
    ctypedef AreaPtr ConstAreaPtr "const shared_ptr<const Osmium::OSM::Area>"

    NodePtr &castNodePtr "boost::static_pointer_cast<const Osmium::OSM::Node>"(ObjectPtr&)
    WayPtr &castWayPtr "boost::static_pointer_cast<const Osmium::OSM::Way>"(ObjectPtr&)
    RelationPtr &castRelationPtr "boost::static_pointer_cast<const Osmium::OSM::Relation>"(ObjectPtr&)
    AreaPtr &castAreaPtr "boost::static_pointer_cast<const Osmium::OSM::Area>"(ObjectPtr&)
