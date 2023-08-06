"""test_namespace module"""

import unittest
from namespace import Namespace, as_namespace


class TestNamespace(unittest.TestCase):

    # ABC interfaces
    MutableMappingAttrs = ("__setitem__", "__delitem__",
                           "pop", "popitem", "clear", "update", "setdefault")
    MappingAttrs = ("__getitem__", "__contains__", "__eq__", "__ne__",
                    "keys", "items", "values", "get")
    BaseAttrs = ("__len__", "__iter__", "__contains__")

    D = {"x": 1, "y": 2}

    def _verify(self, ns):
        self.assertIsInstance(ns, Namespace)
        self.assertEqual(dir(ns), sorted(dict.keys(ns)))
        self.assertEqual(ns, self.D)

    def test_mapping(self):
        ns = Namespace(self.D)

        self.assertEqual(dict(**ns), self.D)

        for name in self.BaseAttrs:
            self.assertTrue(hasattr(type(ns), name))
        for name in self.MappingAttrs:
            self.assertTrue(hasattr(type(ns), name))
        for name in self.MutableMappingAttrs:
            self.assertTrue(hasattr(type(ns), name))

        self.assertEqual(ns, self.D)
        self.assertEqual(self.D, ns)
        self.assertFalse(ns is self.D)

        self.assertEqual(ns["x"], self.D["x"])
        self.assertEqual(ns.x, self.D["x"])

        ns["z"] = 9
        self.assertIn("z", ns)
        self.assertEqual(ns.z, 9)
        self.assertNotIn("z", self.D)
        del ns["z"]
        self.assertNotIn("z", ns)

    def test_not_mapping(self):
        ns = Namespace(self.D)

        with self.assertRaises(ValueError):
            dict(ns)

        for name in self.BaseAttrs:
            self.assertFalse(hasattr(ns, name))
        for name in self.MappingAttrs:
            self.assertFalse(hasattr(ns, name))
        for name in self.MutableMappingAttrs:
            self.assertFalse(hasattr(ns, name))

    def test_creation(self):
        ns = Namespace(self.D)
        self._verify(ns)

        ns = Namespace.from_mapping(self.D)
        self._verify(ns)

        ns = Namespace.from_sequence(self.D.items())
        self._verify(ns)

        class NS:
            x = self.D["x"]
            y = self.D["y"]
        ns = Namespace.from_object(NS, names=tuple(self.D))
        self._verify(ns)

        class NS:
            def __init__(self, **kwargs):
                for name in kwargs:
                    setattr(self, name, kwargs[name])
        ns = Namespace.from_object(NS(**self.D), names=tuple(self.D))
        self._verify(ns)

    def test_as_namespace(self):

        ns = as_namespace(self.D)
        self._verify(ns)

        ns = as_namespace(tuple(self.D.items()))
        self._verify(ns)

        @as_namespace
        class ns:
            x = self.D["x"]
            y = self.D["y"]
        self._verify(ns)

        class NS:
            def __init__(self, **kwargs):
                for name in kwargs:
                    setattr(self, name, kwargs[name])
        ns = as_namespace(NS(**self.D), names=tuple(self.D))

if __name__ == "__main__":
    unittest.main()
