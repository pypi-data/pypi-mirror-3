from unittest import TestCase
import os
from pprint import pprint

import osmium

datadir = os.path.join(os.path.dirname(__file__), 'data')

class Keeper(osmium.handler.Base):
    """Simple handler, which saves every OSM object
    """
    def __init__(self):
        self.meta = None
        self.nodes = []
        self.ways =  []
        self.rels =  []

    def init(self, meta):
        self.meta = meta

    def node(self, node):
        self.nodes.append(node)

    def way(self, way):
        self.ways.append(way)

    def relation(self, rel):
        self.rels.append(rel)

def setUpModule():
    global keeper
    keeper= Keeper()
    infile = osmium.OSMFile(os.path.join(datadir,'example.osm').encode('utf8'))
    infile.read(keeper)


class TestObject(TestCase):

    def test_simple_fields(self):
        """test simple fields of OSM objects
        """
        self.assertEqual(keeper.nodes[0].id_, 1)
        self.assertEqual(keeper.nodes[1].id_, 2)
        self.assertEqual(keeper.ways[0].id_, 7)
        self.assertEqual(keeper.rels[0].id_, 9)

        self.assertEqual(keeper.nodes[0].version, 1)
        self.assertEqual(keeper.ways[0].changeset, 123456)
        self.assertEqual(keeper.rels[0].uid, 31337)
        self.assertEqual(keeper.nodes[1].timestamp, 1330517624)
        self.assertEqual(keeper.ways[1].endtime, 0)
        self.assertEqual(keeper.nodes[2].user, 'haxor')
        self.assertEqual(keeper.nodes[3].visible, True)

    def test_tags(self):
        """test tags property
        """

        tl = keeper.nodes[0].tags
        self.assertEqual(len(tl), 0)

        tl = keeper.ways[0].tags
        self.assertDictEqual(dict(tl), {'name': 'Liedenbrocksches Meer', 'natural': 'water'})

class TestTagList(TestCase):
    def setUp(self):
        self.empty = keeper.nodes[0].tags
        self.ex = keeper.ways[0].tags

    def test_len(self):
        self.assertEqual(len(keeper.nodes[0].tags), 0)
        self.assertEqual(len(keeper.ways[0].tags), 2)

    def test_str(self):
        self.assertEqual(str(keeper.nodes[0].tags), '{}')
        self.assertEqual(str(keeper.ways[0].tags), "{'name': 'Liedenbrocksches Meer', 'natural': 'water'}")

    def test_repr(self):
        self.assertRegex(repr(keeper.nodes[0].tags), '^<osmium\.osm\.TagList object at 0x[0-9a-f]+>$')
        self.assertRegex(repr(keeper.ways[0].tags), '^<osmium\.osm\.TagList object at 0x[0-9a-f]+>$')

    def test_getitem(self):
        self.assertEqual(self.ex['natural'], 'water')
        self.assertRaises(KeyError, lambda :self.empty['name'])

    def test_keys(self):
        self.assertEqual(list(self.ex.keys()), ['name', 'natural'])
        self.assertEqual(list(self.empty.keys()), [])

    def test_iter(self):
        self.assertEqual(list(self.ex), ['name', 'natural'])
        self.assertEqual(list(self.empty), [])

    def test_values(self):
        self.assertEqual(list(self.ex.values()), ['Liedenbrocksches Meer', 'water'])
        self.assertEqual(list(self.empty.values()), [])

    def test_items(self):
        self.assertEqual(list(self.ex.items()), [('name', 'Liedenbrocksches Meer'), ('natural', 'water')])
        self.assertEqual(list(self.empty.values()), [])

class TestNode(TestCase):
    def test_simple_fields(self):
        """test simple fields of nodes
        """
        self.assertAlmostEqual(keeper.nodes[0].lon, -0.0032339)
        self.assertAlmostEqual(keeper.nodes[0].lat, -0.0041772)

class TestWay(TestCase):
    def setUp(self):
        self.way = keeper.ways[0]

    def test_len(self):
        self.assertEqual(len(self.way.nodes), 4)

    def test_str(self):
        self.assertEqual(str(self.way.nodes), '[3, 2, 1, 3]')

    def test_getitem(self):
        self.assertEqual(self.way.nodes[0], 3)
        self.assertRaises(IndexError, lambda: self.way.nodes[5])

    def test_iter(self):
        self.assertEqual(list(self.way.nodes), [3, 2, 1, 3])

class TestRelation(TestCase):
    def setUp(self):
        self.rel = keeper.rels[0]

    def test_len(self):
        self.assertEqual(len(self.rel.members), 3)

    def test_getitem(self):
        self.assertEqual(self.rel.members[0], (7, 'w', ''))
        self.assertEqual(self.rel.members[2], (6, 'n', 'nametag'))

    def test_str(self):
        self.assertEqual(str(self.rel.members), "[(7, 'w', ''), (8, 'w', ''), (6, 'n', 'nametag')]")

    def test_iter(self):
        self.assertEqual(list(self.rel.members), [(7, 'w', ''), (8, 'w', ''), (6, 'n', 'nametag')])

class TestMeta(TestCase):

    def test_multiple_versions(self):
        self.assertEqual(keeper.meta.has_multiple_object_versions, False)

class TestBounds(TestCase):

    def test_properties(self):
        self.assertEqual(keeper.meta.bounds.defined, True)
        self.assertAlmostEqual(keeper.meta.bounds.bottom, -0.0042670)
        self.assertAlmostEqual(keeper.meta.bounds.left,   -0.0076357)
        self.assertAlmostEqual(keeper.meta.bounds.top,     0.0153163)
        self.assertAlmostEqual(keeper.meta.bounds.right,  -0.0032339)
