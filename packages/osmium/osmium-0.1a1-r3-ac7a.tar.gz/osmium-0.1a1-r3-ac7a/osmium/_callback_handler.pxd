from c_osmium.handler cimport Base as c_Base
from c_osmium.osm cimport Node
from osmium.handler cimport Base

cdef extern from "_callback_handler.hpp":
    cdef cppclass CallbackHandler(c_Base):
        CallbackHandler(Base)
