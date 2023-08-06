from unittest import TestCase, skip, expectedFailure
import os
import tempfile
import shutil

import osmium

datadir = os.path.join(os.path.dirname(__file__), 'data')

def setUpModule():
    global tempdir 
    tempdir = tempfile.mkdtemp()

def tearDownModule():
    global tempdir
    shutil.rmtree(tempdir)


class TestOsmium(TestCase):

    def test_debug(self):
        """test osmium.debug and osmium.set_debug
        """
        self.assertEqual(osmium.debug(), True)
        osmium.set_debug(False)
        self.assertEqual(osmium.debug(), False)
        osmium.set_debug(True)
        self.assertEqual(osmium.debug(), True)

class TestOSMFile(TestCase):

    @expectedFailure
    def test_init(self):
        """test initialization from bytes and strings
        """
        osmfile = osmium.OSMFile(b'simple.osm.pbf')
        self.assertEqual(osmfile.filename, b'simple.osm.pbf')

        osmfile = osmium.OSMFile('simple.osm.pbf')
        self.assertEqual(osmfile.filename, 'simple.osm.pbf')

    def test_encoding(self):
        """test get_encoding method
        """
        osmfile = osmium.OSMFile(b'simple.osm.pbf')
        self.assertEqual(osmfile.get_encoding(), osmfile.ENC_PBF)

        osmfile = osmium.OSMFile(b'simple.osm')
        self.assertEqual(osmfile.get_encoding(), osmfile.ENC_XML)

        osmfile = osmium.OSMFile(b'simple.osm.gz')
        self.assertEqual(osmfile.get_encoding(), osmfile.ENC_XMLgz)

        osmfile = osmium.OSMFile(b'simple.osm.bz2')
        self.assertEqual(osmfile.get_encoding(), osmfile.ENC_XMLbz2)


    def test_type(self):
        """test get_type method
        """
        osmfile = osmium.OSMFile(b'simple.osm')
        self.assertEqual(osmfile.get_type(), osmfile.TYPE_OSM)

        osmfile = osmium.OSMFile(b'simple.osh')
        self.assertEqual(osmfile.get_type(), osmfile.TYPE_HISTORY)
        
        osmfile = osmium.OSMFile(b'simple.osc')
        self.assertEqual(osmfile.get_type(), osmfile.TYPE_CHANGE)

    def test_set_type_and_encoding(self):
        """test set_type_and_encoding
        """
        osmfile = osmium.OSMFile(b'simple.osm.pbf')
        self.assertEqual(osmfile.get_encoding(), osmfile.ENC_PBF)

        osmfile.set_type_and_encoding(b'osm.bz2')
        self.assertEqual(osmfile.get_encoding(), osmfile.ENC_XMLbz2)

        osmfile.set_type_and_encoding(b'osm')
        self.assertEqual(osmfile.get_encoding(), osmfile.ENC_XML)

    def test_file_copy(self):
        """process a file without changing
        """
        global tempdir
        infile = osmium.OSMFile(os.path.join(datadir,'example.osm').encode('utf8'))
        outfile = osmium.OSMFile(os.path.join(tempdir, 'example.osm').encode('utf8'))
        handler = outfile.create_output_file()

        infile.read(handler)

        assert( os.path.isfile(os.path.join(tempdir, 'example.osm')))
        self.assertEqualTextFile( os.path.join(datadir, 'example.osm'), os.path.join(tempdir, 'example.osm'))

    def test_file_convert(self):
        """convert osm to pbf
        """
        global tempdir
        osmium.set_debug(False)
        infile = osmium.OSMFile(os.path.join(datadir,'example.osm').encode('utf8'))
        outfile = osmium.OSMFile(os.path.join(tempdir, 'example.osm.pbf').encode('utf8'))
        handler = outfile.create_output_file()

        infile.read(handler)

        assert( os.path.isfile(os.path.join(tempdir, 'example.osm.pbf')))
        self.assertEqualFile( os.path.join(datadir, 'example.osm.pbf'), os.path.join(tempdir, 'example.osm.pbf'))
        osmium.set_debug(True)

    def test_file_convert_and_back(self):
        """convert osm to pbf and back
        """
        global tempdir
        osmium.set_debug(False)
        infile = osmium.OSMFile(os.path.join(datadir,'example.osm').encode('utf8'))
        outfile = osmium.OSMFile(os.path.join(tempdir, 'example.osm.pbf').encode('utf8'))
        handler = outfile.create_output_file()
        infile.read(handler)

        infile = osmium.OSMFile(os.path.join(tempdir, 'example.osm.pbf').encode('utf8'))
        outfile = osmium.OSMFile(os.path.join(tempdir, 'example2.osm').encode('utf8'))
        handler = outfile.create_output_file()
        infile.read(handler)

        self.assertEqualTextFile( os.path.join(datadir, 'example.osm'), os.path.join(tempdir, 'example2.osm'))
        osmium.set_debug(True)
    

    def assertEqualFile(self, file1, file2):
        """compare two binary files
        """
        with open(file1, 'rb') as infile:
            file1content = infile.read()

        with open(file2, 'rb') as infile:
            file2content = infile.read()

        self.assertEqual(file1content, file2content)

    def assertEqualTextFile(self, file1, file2):
        """compare two text files
        """
        with open(file1, 'rt') as infile:
            file1content = infile.read()

        with open(file2, 'rt') as infile:
            file2content = infile.read()

        self.assertMultiLineEqual(file1content, file2content)
