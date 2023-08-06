import unittest

import sqlalchemy

from lazy_slides.cache import open_cache

from lazy_slides.tests.util import (remove, temp_file)

class CacheTest(unittest.TestCase):

    def setUp(self):
        self.db_file = ':memory:'
    #     remove(self.db_file)

    # def tearDown(self):
    #     remove(self.db_file)

    def test_get(self):
        engine = 'engine'
        tag = 'tag'
        filename = 'test_file'

        with open_cache(self.db_file, 1000) as cache:
            self.assertEqual(cache.get(engine, tag), None)

            with temp_file(filename):
                cache.set(engine, tag, filename)

                self.assertEqual(cache.get(engine, tag), filename)

    def test_get_missing_file(self):
        engine = 'engine'
        tag = 'tag'
        filename = 'test_file'

        with open_cache(self.db_file, 100) as cache:

            with temp_file(filename):
                cache.set(engine, tag, filename)

                self.assertEqual(cache.get(engine, tag), filename)

            self.assertEqual(cache.get(engine, tag), None)

    def test_set_overwrite(self):
        engine = 'engine'
        tag = 'tag'
        filename = 'temp_file'
        filename2 = 'temp_file2'

        with open_cache(self.db_file, 1000) as cache:
            with temp_file(filename):
                cache.set(engine, tag, filename)
                self.assertEqual(cache.get(engine, tag), filename)

            with temp_file(filename2):
                cache.set(engine, tag, filename2)
                self.assertEqual(cache.get(engine, tag), filename2)

    def test_size(self):
        with open_cache(self.db_file, 1000) as cache:
            self.assertEqual(cache.size(), 0)

            for i in range(100):
                cache.set('engine', str(i), str(i))
                self.assertEqual(cache.size(), i + 1)

    def test_trim(self):
        SIZE = 100

        with open_cache(self.db_file, 1000) as cache:
            for i in range(SIZE):
                cache.set('engine', str(i), str(i))

            self.assertEqual(cache.size(), SIZE)

            NEW_SIZE=40
            cache.trim(NEW_SIZE)
            self.assertEqual(cache.size(), NEW_SIZE)

            cache.trim(cache.size() + 1)
            self.assertEqual(cache.size(), NEW_SIZE)
