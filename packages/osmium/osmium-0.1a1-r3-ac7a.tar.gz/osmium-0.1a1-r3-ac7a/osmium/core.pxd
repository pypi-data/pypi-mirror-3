from libcpp cimport bool
from c_osmium.osmfile cimport OSMFile as c_OSMFile
from osmium cimport handler
from osmium cimport output

cdef enum FileType:
    C_TYPE_OSM,
    C_TYPE_HISTORY,
    C_TYPE_CHANGE,
    C_TYPE_EXCEPTION
cdef enum FileEncoding:
    C_ENC_PBF,
    C_ENC_XML,
    C_ENC_XMLgz,
    C_ENC_XMLbz2,
    C_ENC_EXCEPTION

cdef class OSMFile:
    u"""This class describes an OSM file in one of several formats.
    It can be used as factory class for generating input and output OSM files.

    If the filename is empty, this means stdin or stdout is used. If you set
    the filename to "-" it will be treated the same.
    """
    cdef c_OSMFile *c_osmfile

    cpdef read(self, handler.Base handler)
    cpdef set_type_and_encoding(self, char* suffix)
    cpdef close(self)
    cpdef int get_fd(self) except? -1
    cpdef FileType get_type(self) except? C_TYPE_EXCEPTION
    cpdef set_type(self, FileType newtype)
    cpdef FileEncoding get_encoding(self) except? C_ENC_EXCEPTION
    cpdef set_encoding(self, FileEncoding newenc)
    cpdef output.Base create_output_file(self)

cpdef set_debug(bool d)
cpdef bool debug()

