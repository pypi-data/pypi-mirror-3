#ifndef __PYX_HAVE__osmium__core
#define __PYX_HAVE__osmium__core

struct StopReading_struct;

/* "osmium/core.pxd":46
 * cpdef bool debug()
 * 
 * cdef public class StopReading(Exception) [object StopReading_struct, type StopReading_type]:             # <<<<<<<<<<<<<<
 *     """raise this exception to immediately stop reading the input file
 *     """
 */
struct StopReading_struct {
  PyBaseExceptionObject __pyx_base;
};

#ifndef __PYX_HAVE_API__osmium__core

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) StopReading_type;

#endif /* !__PYX_HAVE_API__osmium__core */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initcore(void);
#else
PyMODINIT_FUNC PyInit_core(void);
#endif

#endif /* !__PYX_HAVE__osmium__core */
