from unittest import TestCase
import os

import osmium

datadir = os.path.join(os.path.dirname(__file__), 'data')

class CheckCalledHandler(osmium.handler.Base):
    """Basic handler, records which functions are called
    """

    def __init__(self):
        self.called = []

    def init(self, meta):
        self.called.append('init')

    def node(self, node):
        self.called.append('node '+str(node.id_))

    def way(self, way):
        self.called.append('way '+str(way.id_))

    def relation(self, rel):
        self.called.append('rel '+str(rel.id_))

    def before_nodes(self):
        self.called.append('bn')
    def after_nodes(self):
        self.called.append('an')
    def before_ways(self):
        self.called.append('bw')
    def after_ways(self):
        self.called.append('aw')
    def before_relations(self):
        self.called.append('br')
    def after_relations(self):
        self.called.append('ar')
    def final(self):
        self.called.append('final')

class CheckCalledStopHandler(CheckCalledHandler):
    def after_nodes(self):
        CheckCalledHandler.after_nodes(self)
        raise osmium.handler.StopReading

def setUpModule():
    global infile
    infile = osmium.OSMFile(os.path.join(datadir, 'example.osm').encode('utf-8'))

class TestPythonHandler(TestCase):

    def test_method_calls(self):
        check = CheckCalledHandler()
        infile.read(check)

        self.assertEqual(check.called, [
            'init',
            'bn',
            'node 1', 'node 2', 'node 3', 'node 4', 'node 5', 'node 6',
            'an',
            'bw',
            'way 7', 'way 8', 'aw',
            'br',
            'rel 9',
            'ar',
            'final'
            ])

    def test_StopReading(self):
        check = CheckCalledStopHandler()
        infile.read(check)

        self.assertEqual(check. called, [
            'init',
            'bn',
            'node 1', 'node 2', 'node 3', 'node 4', 'node 5', 'node 6',
            'an',
            'final'
            ])

class TestForwardHandler(TestCase):

    def test_called(self):
        check = CheckCalledHandler()
        forwarder = osmium.handler.Forward(check)
        infile.read(forwarder)

        self.assertEqual(check.called, [
            'init',
            'bn',
            'node 1', 'node 2', 'node 3', 'node 4', 'node 5', 'node 6',
            'an',
            'bw',
            'way 7', 'way 8', 'aw',
            'br',
            'rel 9',
            'ar',
            'final'
            ])

class TestTeeHandler(TestCase):

    def test_called(self):
        check1 = CheckCalledHandler()
        check2 = CheckCalledHandler()
        tee = osmium.handler.Tee(check1, check2)
        infile.read(tee)

        self.assertEqual(check1.called, [
            'init',
            'bn',
            'node 1', 'node 2', 'node 3', 'node 4', 'node 5', 'node 6',
            'an',
            'bw',
            'way 7', 'way 8', 'aw',
            'br',
            'rel 9',
            'ar',
            'final'
            ])
        self.assertEqual(check2.called, [
            'init',
            'bn',
            'node 1', 'node 2', 'node 3', 'node 4', 'node 5', 'node 6',
            'an',
            'bw',
            'way 7', 'way 8', 'aw',
            'br',
            'rel 9',
            'ar',
            'final'
            ])
