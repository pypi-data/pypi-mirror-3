import os
import unittest

import collect


class Test01Connection(unittest.TestCase):
    def test_01_connection_without_uri(self):
        connection = collect.connect()
        self.assertEqual(connection._uri, collect.settings.DEFAULT_SERVER_URI)
        
    def test_02_connection_with_uri(self):
        connection = collect.connect(uri="http://localhost:5984/")
        self.assertEqual(connection._uri, "http://localhost:5984/")


class Test02Collections(unittest.TestCase):
    COLLECTION_NAME="test_%s" % os.getpid()
    
    def setUp(self):
        self._connection = collect.connect(uri="http://localhost:5984/")
    
    def tearDown(self):
        self._collection.remove()
    
    def test_01_collection_creation(self):
        self._collection = self._connection.collection(self.COLLECTION_NAME)
        self.assertEqual(self._collection.name, self.COLLECTION_NAME)


class Test03Collect(unittest.TestCase):
    COLLECTION_NAME="test_%s" % os.getpid()
    
    def setUp(self):
        self._connection = collect.connect(uri="http://localhost:5984/")
        self._collection = self._connection.collection(self.COLLECTION_NAME)
    
    def tearDown(self):
        self._collection.remove()
    
    def test_01_collect_dict(self):
        res = self._collection.collect({"temperature": 39.7})
        self.assertTrue(isinstance(res, unicode))
        self.assertEqual(len(res), 32)
    
    def test_02_collect_nondict(self):
        self.assertRaises(TypeError, self._collection.collect, 39.7)
    
    def test_03_collect_empty_dict(self):
        self.assertRaises(TypeError, self._collection.collect, {})


def get_suite():
    "Return a unittest.TestSuite."
    import collect.tests
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(collect.tests)
    return suite