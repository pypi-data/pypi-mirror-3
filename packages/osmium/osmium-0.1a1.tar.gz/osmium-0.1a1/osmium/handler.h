#ifndef __PYX_HAVE__osmium__handler
#define __PYX_HAVE__osmium__handler

struct StopReading_struct;
struct osmhandler_struct;

/* "osmium/handler.pxd":11
 *         pass
 * 
 * cdef public class StopReading(Exception) [object StopReading_struct, type StopReading_type]:             # <<<<<<<<<<<<<<
 *     """raise this exception to immediately stop reading the input file
 *     """
 */
struct StopReading_struct {
  PyBaseExceptionObject __pyx_base;
};

/* "osmium/handler.pxd":16
 *     pass
 * 
 * cdef public class Base[object osmhandler_struct, type osmhandler_type]:             # <<<<<<<<<<<<<<
 *     """base class for python implemented handlers
 *     """
 */
struct osmhandler_struct {
  PyObject_HEAD
  struct __pyx_vtabstruct_6osmium_7handler_Base *__pyx_vtab;
  struct __pyx_obj_6osmium_3osm_Node *cur_node;
};

#ifndef __PYX_HAVE_API__osmium__handler

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) StopReading_type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) osmhandler_type;

__PYX_EXTERN_C DL_IMPORT(int) c_init_callback(struct osmhandler_struct *, Osmium::OSM::Meta &);
__PYX_EXTERN_C DL_IMPORT(int) c_before_nodes_callback(struct osmhandler_struct *);
__PYX_EXTERN_C DL_IMPORT(int) c_after_nodes_callback(struct osmhandler_struct *);
__PYX_EXTERN_C DL_IMPORT(int) c_before_ways_callback(struct osmhandler_struct *);
__PYX_EXTERN_C DL_IMPORT(int) c_after_ways_callback(struct osmhandler_struct *);
__PYX_EXTERN_C DL_IMPORT(int) c_before_relations_callback(struct osmhandler_struct *);
__PYX_EXTERN_C DL_IMPORT(int) c_after_relations_callback(struct osmhandler_struct *);
__PYX_EXTERN_C DL_IMPORT(int) c_final_callback(struct osmhandler_struct *);
__PYX_EXTERN_C DL_IMPORT(int) c_node_callback(struct osmhandler_struct *, const shared_ptr<const Osmium::OSM::Node> &);
__PYX_EXTERN_C DL_IMPORT(int) c_way_callback(struct osmhandler_struct *, const shared_ptr<const Osmium::OSM::Way> &);
__PYX_EXTERN_C DL_IMPORT(int) c_relation_callback(struct osmhandler_struct *, const shared_ptr<const Osmium::OSM::Relation> &);

#endif /* !__PYX_HAVE_API__osmium__handler */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC inithandler(void);
#else
PyMODINIT_FUNC PyInit_handler(void);
#endif

#endif /* !__PYX_HAVE__osmium__handler */
