u"""
Cython examples
===============

This module contains some cython implemented example code:

read_file: call default handler on file
debug_read: call debug handler on file
ExampleHandler: cython implemented debug handler
"""
from libcpp.string cimport string

cimport c_osmium
from c_osmium.osmfile cimport OSMFile as c_OSMFile

from osmium.handler cimport Base as osmhandler, Debug as debug_handler
from osmium.handler import Base as osmhandler, Debug as debug_handler
from osmium.handler cimport Meta, Node, Way, Relation

def read_file(name):
    u"""read_file(name)
    Read the file **name** and process it through the default osmhandler.
    """
    c_osmium.init(True)

    cdef char * namecstr = name
    cdef string namestr
    namestr.assign(namecstr)
    cdef c_OSMFile *infile = new c_OSMFile(namestr)
    cdef osmhandler python_handler = osmhandler()

    python_handler.handle_infile(infile)

def debug_read(name):
    u"""debug_read(name)
    Read the file **name** and process it through the Osmium debug handler.
    """
    c_osmium.init(True)

    cdef char * namecstr = name
    cdef string namestr
    namestr.assign(namecstr)
    cdef c_OSMFile *infile = new c_OSMFile(namestr)

    cdef osmhandler python_handler = debug_handler()

    python_handler.handle_infile(infile)

cdef class ExampleHandler(osmhandler):
    u"""Example of a cython implemented handler

    Print debugging messages on each callback and save one 
    copy of each object type.
    """
    cdef public Node saved_node
    cdef public Way saved_way
    cdef public Relation saved_relation

    cpdef init(self, Meta curmeta):
        print("INIT:")
        print(curmeta)

    cpdef before_nodes(self):
        print("BEFORE NODES")

    cpdef node(self, Node curnode):
        """node_callback(self, curnode)
        default handler for nodes
        """
        print("NODE:")
        print("object-id: ", curnode.c_object[0].get().o_id())
        print("address: ", <long>curnode.c_object[0].get())
        if curnode.tags:
            self.saved_node = curnode
        print(curnode.tags)

    cpdef after_nodes(self):
        print("AFTER NODES")

    cpdef before_ways(self):
        print("BEFORE WAYS")

    cpdef way(self, Way curway):
        print("WAY:")
        print("object-id:", curway.c_object[0].get().o_id())
        print("address:",   <long>curway.c_object[0].get())
        print(curway.tags)
        print(curway.nodes)
        self.saved_way = curway

    cpdef after_ways(self):
        print("AFTER WAYS")

    cpdef before_relations(self):
        print("BEFORE RELATIONS")

    cpdef relation(self, Relation currel):
        print("RELATION:")
        print(currel.tags)
        print(currel.members)
        self.saved_relation = currel

    cpdef after_relations(self):
        print("AFTER RELATIONS")
    
    cpdef final(self):
        print("FINAL")
