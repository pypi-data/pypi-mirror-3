# 
from libcpp cimport bool

cdef extern from "osmium.hpp" namespace "Osmium":
    cdef cppclass Framework:
        Framework(bool)

    cdef Framework init(bool)
    cdef void set_debug(bool)
    cdef bool debug()
