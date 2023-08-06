from c_osmium.output cimport Base as c_Base
from c_osmium.osmfile cimport OSMFile as c_OSMFile

from osmium cimport handler

cdef class Base(handler.Base):
    cdef c_Base* c_output
