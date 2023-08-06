# coding: utf-8
# Copyright 2012 litl, LLC. All Rights Reserved.

import operator
import os
import unittest2 as unittest

import park


class KVStoreBase(object):
    """Base tests for KV Stores"""

    def test_get_default(self):
        self.assertIsNone(self.store.get("missing"))

    def test_put_get(self):
        key, value = "test_key", "test_value"

        self.assertIsNone(self.store.get(key, None))
        self.store.put(key, value)

        self.assertTrue(self.store.contains(key))
        self.assertEqual(value, self.store.get(key))

    def test_delete(self):
        self.store.put("test_key1", "test_value1")
        self.store.put("test_key2", "test_value2")

        self.store.delete("test_key1")

        self.assertEqual(["test_key2"], list(self.store.keys()))

    def test_delete_many(self):
        self.store.put("test_key1", "test_value1")
        self.store.put("test_key2", "test_value2")

        self.store.delete_many(["test_key1", "test_key2"])

        self.assertEqual([], list(self.store.keys()))

    def test_null_key(self):
        key, value = "\x00", "test_value"

        self.assertIsNone(self.store.get(key, None))
        self.store.put(key, value)

        self.assertEqual(value, self.store.get(key))

        self.assertEqual([key], list(self.store.keys()))
        self.assertEqual([(key, value)], list(self.store.items()))

    def test_null_value(self):
        key, value = "test_key", "\x00"

        self.assertIsNone(self.store.get(key, None))
        self.store.put(key, value)

        self.assertEqual(value, self.store.get(key))

        self.assertEqual([key], list(self.store.keys()))
        self.assertEqual([(key, value)], list(self.store.items()))

    def test_replace(self):
        key = "foo"
        self.assertIsNone(self.store.get(key, None))

        self.store.put(key, "bar")
        self.assertEqual("bar", self.store.get(key))

        self.store.put(key, "baz")
        self.assertEqual("baz", self.store.get(key))

    def test_put_many(self):
        items = [
            ("one", "value1"),
            ("two", "value2"),
            ("three", "value3"),
            ("four", "value4"),
            ("five", "value5"),
            ("six", "value6"),
            ("seven", "value7"),
            ("eight", "value8"),
            ("nine", "value9")
        ]

        self.store.put_many(items)

        for key, value in items:
            self.assertEqual(value, self.store.get(key))

    def test_no_keys(self):
        self.assertEqual([], list(self.store.keys()))

        self.assertEqual([], list(self.store.keys(key_from="foo")))
        self.assertEqual([], list(self.store.keys(key_to="bar")))

        self.assertEqual([], list(self.store.keys(key_from="foo",
                                                  key_to="bar")))

    def test_no_items(self):
        self.assertEqual([], list(self.store.items()))

        self.assertEqual([], list(self.store.items(key_from="foo")))
        self.assertEqual([], list(self.store.items(key_to="bar")))

        self.assertEqual([], list(self.store.items(key_from="foo",
                                                   key_to="bar")))

    def test_keys(self):
        items = [
            ("one", "value1"),
            ("two", "value2"),
            ("three", "value3"),
            ("four", "value4"),
            ("five", "value5"),
            ("six", "value6"),
            ("seven", "value7"),
            ("eight", "value8"),
            ("nine", "value9")
        ]

        for key, value in items:
            self.store.put(key, value)

        # Sorted order is: eight five four nine one seven six three two
        keys = list(self.store.keys())
        expected = "eight five four nine one seven six three two".split()
        self.assertEqual(expected, keys)

        # Test key_from on keys that are present and missing in the db
        keys = list(self.store.keys(key_from="four"))
        expected = "four nine one seven six three two".split()
        self.assertEqual(expected, keys)

        keys = list(self.store.keys(key_from="fo"))
        expected = "four nine one seven six three two".split()
        self.assertEqual(expected, keys)

        # Test key_to
        keys = list(self.store.keys(key_to="six"))
        expected = "eight five four nine one seven six".split()
        self.assertEqual(expected, keys)

        keys = list(self.store.keys(key_to="si"))
        expected = "eight five four nine one seven".split()
        self.assertEqual(expected, keys)

        # And test them both together
        keys = list(self.store.keys(key_from="five", key_to="three"))
        expected = "five four nine one seven six three".split()
        self.assertEqual(expected, keys)

    def test_prefix_keys(self):
        # Fake some interesting keys and values to make sure the
        # prefix iterators are working
        store = self.store

        store.put("a/", "a")
        store.put("a/b", "b")
        store.put("a/c", "c")
        store.put("a/d", "d")
        store.put("a/e", "e")
        store.put("a/f", "f")
        store.put("b/", "b")
        store.put("c/", "c")
        store.put("d/", "d")

        a_list = list(store.prefix_keys("a/"))
        self.assertEqual("a/ a/b a/c a/d a/e a/f".split(), a_list)

        a_list = list(store.prefix_keys("a/", strip_prefix=True))
        self.assertEqual(["", "b", "c", "d", "e", "f"], a_list)

        self.assertEqual(["b/"], list(store.prefix_keys("b/")))
        self.assertEqual(["c/"], list(store.prefix_keys("c/")))
        self.assertEqual(["d/"], list(store.prefix_keys("d/")))

    def test_items(self):
        put_items = dict([
            ("one", "value1"),
            ("two", "value2"),
            ("three", "value3"),
            ("four", "value4"),
            ("five", "value5"),
            ("six", "value6"),
            ("seven", "value7"),
            ("eight", "value8"),
            ("nine", "value9")
        ])

        for key, value in put_items.items():
            self.store.put(key, value)

        # Sorted order is: eight five four nine one seven six three two
        keys = list(self.store.items())
        expected = sorted(put_items.items(), key=operator.itemgetter(0))
        self.assertEqual(expected, keys)

        # Test key_from on keys that are present and missing in the db
        keys = list(self.store.items(key_from="four"))
        self.assertEqual(expected[2:], keys)

        keys = list(self.store.items(key_from="fo"))
        self.assertEqual(expected[2:], keys)

        # Test key_to
        keys = list(self.store.items(key_to="six"))
        self.assertEqual(expected[:7], keys)

        keys = list(self.store.items(key_to="si"))
        self.assertEqual(expected[:6], keys)

        # And test them both together
        keys = list(self.store.items(key_from="five", key_to="three"))
        self.assertEqual(expected[1:8], keys)

    def test_prefix_items(self):
        # Fake some interesting keys and values to make sure the
        # prefix iterators are working
        store = self.store

        store.put("a/", "a")
        store.put("a/b", "b")
        store.put("a/c", "c")
        store.put("a/d", "d")
        store.put("a/e", "e")
        store.put("a/f", "f")
        store.put("b/", "b")
        store.put("c/", "c")
        store.put("d/", "d")

        expected = [("a/", "a"),
                    ("a/b", "b"),
                    ("a/c", "c"),
                    ("a/d", "d"),
                    ("a/e", "e"),
                    ("a/f", "f")]

        a_list = list(store.prefix_items("a/"))
        self.assertEqual(expected, a_list)

        expected = [("", "a"),
                    ("b", "b"),
                    ("c", "c"),
                    ("d", "d"),
                    ("e", "e"),
                    ("f", "f")]

        a_list = list(store.prefix_items("a/", strip_prefix=True))
        self.assertEqual(expected, a_list)

    def testContextManager(self):
        with self.store as kv:
            kv.put("foo", "bar")
            kv.put("baz", "quux")

            self.assertEqual("bar", kv.get("foo"))


class TestIbatch(unittest.TestCase):
    def test_ibatch(self):
        items = range(10)

        batches = park.ibatch(items, 3)

        self.assertEqual([0, 1, 2], list(next(batches)))
        self.assertEqual([3, 4, 5], list(next(batches)))
        self.assertEqual([6, 7, 8], list(next(batches)))
        self.assertEqual([9], list(next(batches)))


class TestSQLiteStore(unittest.TestCase, KVStoreBase):
    DB = "tests.test_sqlite_store"

    def setUp(self):
        self.store = park.SQLiteStore(self.DB)

        def cleanup():
            if os.path.exists(self.DB):
                os.unlink(self.DB)

        self.addCleanup(cleanup)
