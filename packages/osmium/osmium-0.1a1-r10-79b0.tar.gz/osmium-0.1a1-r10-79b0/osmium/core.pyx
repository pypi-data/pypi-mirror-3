u"""
Core components of Osmium
=========================

This module contains the OSMFile factory class and the main Osmium debug switch.
"""
from libcpp.string cimport string

cimport c_osmium
from c_osmium.osmfile cimport OSMFile as c_OSMFile
from c_osmium cimport osmfile



cdef class OSMFile:
    u"""This class describes an OSM file in one of several formats.
    It can be used as factory class for generating input and output OSM files.

    If the filename is empty, this means stdin or stdout is used. If you set
    the filename to "-" it will be treated the same.
    """

    # Define constants for FileType and FileEncoding
    TYPE_OSM = C_TYPE_OSM
    TYPE_HISTORY = C_TYPE_HISTORY
    TYPE_CHANGE = C_TYPE_CHANGE

    ENC_PBF=C_ENC_PBF
    ENC_XML=C_ENC_XML
    ENC_XMLgz=C_ENC_XMLgz
    ENC_XMLbz2=C_ENC_XMLbz2

    def __cinit__(self, filename=b""):
        cdef string fn_string
        fn_string.assign(<char*>filename)
        self.c_osmfile = new c_OSMFile(fn_string)

    def __init__(self, filename=b""):
        u"""__init__(self, filename=b"")
        Create OSMFile using type and encoding from filename. If you want
        to overwrite these settings you can change them later.

        @param filename Filename including suffix. The type and encoding
        of the file will be taken from the suffix.
        An empty filename or "-" means stdin or stdout.
        """
        pass

    def __dealloc__(self):
        del self.c_osmfile

    def copy(self):
        u"""copy(self)
        Create a copy of the OSMFile object.
        Only attributes not related to the open file will be
        copied.
        """
        cdef OSMFile result = OSMFile()
        result.c_osmfile[0] = self.c_osmfile[0]
        return result

    cpdef read(self, handler.Base handler):
        u"""read(self, handler)
        Read OSM file and call methods on handler object
        """
        handler.handle_infile(self.c_osmfile)

    cpdef set_type_and_encoding(self, char* suffix):
        u"""set_type_and_encoding(self, suffix)
        Change type and encoding according to the given suffix.
        """
        cdef string str_suffix 
        str_suffix.assign(suffix)
        self.c_osmfile.set_type_and_encoding(str_suffix)

    cpdef close(self):
        u"""close(self)
        Close the associated file.
        """
        self.c_osmfile.close()

    cpdef int get_fd(self) except? -1:
        u"""get_fd(self) -> int
        Return the associated file descriptor
        """
        return self.c_osmfile.get_fd()

    cpdef FileType get_type(self) except? C_TYPE_EXCEPTION:
        u"""get_type(self) -> FileType
        Return the configured filetype
        """
        cdef osmfile.FileType* c_ft
        c_ft = self.c_osmfile.get_type()
        if c_ft == osmfile.FileTypeOSM():
            return C_TYPE_OSM
        elif c_ft == osmfile.FileTypeHistory():
            return C_TYPE_HISTORY
        elif c_ft == osmfile.FileTypeChange():
            return C_TYPE_CHANGE
        else:
            raise RuntimeError("Unknown Filetype")
    
    cpdef set_type(self, FileType newtype):
        u"""set_type(self, FileType)
        Set the filetype.
        """
        cdef osmfile.FileType* c_ft

        if newtype == C_TYPE_OSM:
            c_ft = osmfile.FileTypeOSM()
        elif newtype == C_TYPE_HISTORY:
            c_ft = osmfile.FileTypeHistory()
        elif newtype == C_TYPE_CHANGE:
            c_ft = osmfile.FileTypeChange()
        else:
            raise RuntimeError("Unknown Filetype")

        self.c_osmfile.set_type(c_ft)

    cpdef FileEncoding get_encoding(self) except? C_ENC_EXCEPTION:
        u"""get_encoding(self) -> FileEncoding
        Get the configured encoding.
 
        Possible values:
            self.ENC_PBF
            self.ENC_XML
            self.ENC_XMLgz
        """
        cdef osmfile.FileEncoding* c_enc
        c_enc = self.c_osmfile.get_encoding()

        if c_enc == osmfile.FileEncodingPBF():
            return C_ENC_PBF
        elif c_enc == osmfile.FileEncodingXML():
            return C_ENC_XML
        elif c_enc == osmfile.FileEncodingXMLgz():
            return C_ENC_XMLgz
        elif c_enc == osmfile.FileEncodingXMLbz2():
            return C_ENC_XMLbz2
        else:
            raise RuntimeError("Unknown Filetype")

    cpdef set_encoding(self, FileEncoding newenc):
        u"""set_encoding(self, FileEncoding)
        Set the encoding for the current file.

        Should be one of
            self.ENC_PBF
            self.ENC_XML
            self.ENC_XMLgz
            self.ENC_XMLbz2
        """
        cdef osmfile.FileEncoding* c_enc

        if newenc == C_ENC_PBF:
            c_enc = osmfile.FileEncodingPBF()
        elif newenc == C_ENC_XML:
            c_enc = osmfile.FileEncodingXML()
        elif newenc == C_ENC_XMLgz:
            c_enc = osmfile.FileEncodingXMLgz()
        elif newenc == C_ENC_XMLbz2:
            c_enc = osmfile.FileEncodingXMLbz2()
        else:
            raise RuntimeError("Unknown Filetype")

        self.c_osmfile.set_encoding(c_enc)

    cpdef output.Base create_output_file(self):
        u"""create_output_file(self) -> Output
        Truncate the file and open it for writing. Returns an Output object.
        """
        cdef output.Base res = output.Base.__new__(output.Base)
        res.c_output = self.c_osmfile.create_output_file()
        if res.c_output is NULL:
            return None
        else:
            return res

cpdef set_debug(bool d):
    u"""set_debug(bool)
    Enable/Disable Osmium debugging messages.

    Default is on.
    """
    c_osmium.set_debug(d)

cpdef bool debug():
    u"""debug()
    Return Osmium debug flag.
    """
    return c_osmium.debug()


# Initialization code
c_osmium.init(True)
