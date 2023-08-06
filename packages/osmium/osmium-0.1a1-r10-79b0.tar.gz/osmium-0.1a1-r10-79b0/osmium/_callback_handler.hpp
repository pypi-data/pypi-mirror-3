#ifndef OSMIUM_CALLBACK_HANDLER_HPP
#define OSMIUM_CALLBACK_HANDLER_HPP

struct osmhandler_struct;

__PYX_EXTERN_C inline int c_init_callback(osmhandler_struct *, Osmium::OSM::Meta&);
__PYX_EXTERN_C inline int c_before_nodes_callback(osmhandler_struct *);
__PYX_EXTERN_C inline int c_node_callback(osmhandler_struct *, const shared_ptr<Osmium::OSM::Node const> &);
__PYX_EXTERN_C inline int c_after_nodes_callback(osmhandler_struct *);
__PYX_EXTERN_C inline int c_before_ways_callback(osmhandler_struct *);
__PYX_EXTERN_C inline int c_way_callback(osmhandler_struct *, const shared_ptr<Osmium::OSM::Way const> &);
__PYX_EXTERN_C inline int c_after_ways_callback(osmhandler_struct *);
__PYX_EXTERN_C inline int c_before_relations_callback(osmhandler_struct *);
__PYX_EXTERN_C inline int c_relation_callback(osmhandler_struct *, const shared_ptr<Osmium::OSM::Relation const> &);
__PYX_EXTERN_C inline int c_after_relations_callback(osmhandler_struct *);
__PYX_EXTERN_C inline int c_final_callback(osmhandler_struct *);

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) StopReading_type;

#define CALLBACK_HANDLE_EXCEPTION(func)                                \
    if (func == 0) {                                                   \
        return;                                                        \
    } else {                                                           \
        if (PyErr_ExceptionMatches((PyObject*)&StopReading_type)) {    \
            PyErr_Clear();                                             \
            throw Osmium::Input::StopReading();                        \
        } else {                                                       \
            throw std::runtime_error("python exception");              \
        }                                                              \
    }

#define CALLBACK_IMPL(name) inline void name () {                      \
    CALLBACK_HANDLE_EXCEPTION(c_##name##_callback(context))            \
}

class CallbackHandler : public Osmium::Handler::Base {
    private:
        osmhandler_struct *context;

    public:
        CallbackHandler(osmhandler_struct *ctx) {
            context = ctx;
        }

        inline void init(Osmium::OSM::Meta& meta) {
            CALLBACK_HANDLE_EXCEPTION(c_init_callback(context, meta))
        }

        CALLBACK_IMPL(before_nodes)

        inline void node(const shared_ptr<Osmium::OSM::Node const> &node) {
            CALLBACK_HANDLE_EXCEPTION(c_node_callback(context, node))
        }

        CALLBACK_IMPL(after_nodes)
        CALLBACK_IMPL(before_ways)

        inline void way(const shared_ptr<Osmium::OSM::Way const> &way) {
            CALLBACK_HANDLE_EXCEPTION(c_way_callback(context, way))
        }

        CALLBACK_IMPL(after_ways)
        CALLBACK_IMPL(before_relations)

        inline void relation(const shared_ptr<Osmium::OSM::Relation const> &relation) {
            CALLBACK_HANDLE_EXCEPTION(c_relation_callback(context, relation))
        }

        CALLBACK_IMPL(after_relations)
        CALLBACK_IMPL(final)
};

#endif
