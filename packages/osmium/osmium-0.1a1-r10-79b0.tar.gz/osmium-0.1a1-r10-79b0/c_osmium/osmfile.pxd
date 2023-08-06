from libcpp cimport bool
from libcpp.string cimport string
from c_osmium cimport handler
from c_osmium cimport output

cdef extern from "osmium/osmfile.hpp" namespace "Osmium::OSMFile":
    cdef cppclass FileType:
        FileType(string, bool)
        string suffix()
        bool has_multiple_object_versions()
    # static methods of FileType
    cdef FileType* FileTypeOSM "Osmium::OSMFile::FileType::OSM"()
    cdef FileType* FileTypeHistory "Osmium::OSMFile::FileType::History"()
    cdef FileType* FileTypeChange "Osmium::OSMFile::FileType::Change"()

    
    cdef cppclass FileEncoding:
        FileEncoding(string, string, string, bool)
        string suffix()
        string compress()
        string decompress()
        bool is_pbf()
    cdef FileEncoding* FileEncodingPBF "Osmium::OSMFile::FileEncoding::PBF"()
    cdef FileEncoding* FileEncodingXML "Osmium::OSMFile::FileEncoding::XML"()
    cdef FileEncoding* FileEncodingXMLgz "Osmium::OSMFile::FileEncoding::XMLgz"()
    cdef FileEncoding* FileEncodingXMLbz2 "Osmium::OSMFile::FileEncoding::XMLbz2"()


cdef extern from "osmium/osmfile.hpp" namespace "Osmium":
    cdef cppclass OSMFile:
        OSMFile() except+
        OSMFile(string) except+
        OSMFile(OSMFile) except+
        void set_type_and_encoding(string) except+
        void close() except+
        void default_settings_for_stdinout() except+
        void default_settings_for_file() except+
        void default_settings_for_url() except+
        int get_fd() 

        FileType* get_type()
        OSMFile& set_type(FileType*)
        OSMFile& set_type(string&)

        bool has_multiple_object_versions()
        FileEncoding* get_encoding()
        OSMFile& set_encoding(FileEncoding*)
        OSMFile& set_encoding(string&)

        OSMFile& set_filename(string&)
        string get_filename()
        string get_filename_without_suffix()
        string get_filename_with_default_suffix()

        void open_for_input() except+
        void open_for_output() except+

        void read(handler.Base) except+
        void read(output.Base) except+
        output.Base* create_output_file() except+
