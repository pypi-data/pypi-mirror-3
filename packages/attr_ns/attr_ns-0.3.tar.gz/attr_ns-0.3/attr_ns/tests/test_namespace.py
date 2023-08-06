
from unittest import TestCase
from collections import OrderedDict

from .. import (get_names, get_namespace_mapping, namespace_repr,
                MappedObject, Namespace, Bunch,
                as_namedtuple)

# XXX can't rely on dict order!


class Test_namespace_repr(TestCase):

    def test_dict(self):
        ns = dict(a=1, c=2, b=4, _c="spam")
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "dict(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "dict(a=1, b=4, c=2)")

    def test_odict(self):
        ns = OrderedDict([('a', 1), ('c', 2), ('b', 4), ('_c', "spam")])
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "OrderedDict(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "OrderedDict(a=1, b=4, c=2)")

    def test_object(self):
        ns = type("NS", (), {})()
        ns.__dict__.update(dict(a=1, c=2, b=4, _c="spam"))
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "type(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "type(a=1, b=4, c=2)")

    def test_type(self):
        ns = type("NS", (), dict(a=1, c=2, b=4, _c="spam"))
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "type(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "type(a=1, b=4, c=2)")

    def test_namespace(self):
        ns = Namespace(a=1, c=2, b=4, _c="spam")
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "Namespace(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "Namespace(a=1, b=4, c=2)")

    def test_slots(self):
        ns = object()
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "object(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "object(a=1, b=4, c=2)")


class TestNamespace(TestCase):

    def test_empty(self):
        ns = Namespace()

        self.assertEqual(len(ns.__dict__), 0)

    def test_args(self):
        with self.assertRaises(TypeError):
            ns = Namespace(1)

    def test_kwargs(self):
        ns = Namespace(x=1, y=2, w=3)

        self.assertEqual(sorted(ns.__dict__.items()),
                         [('w', 3), ('x', 1), ('y', 2)])

    def test_dict(self):
        ns = Namespace(x=1, y=2, w=3)

        self.assertEqual(ns.__dict__, dict(x=1, y=2, w=3))
        self.assertEqual(vars(ns), dict(x=1, y=2, w=3))

    def test_attrget(self):
        ns = Namespace(x=1, y=2, w=3)

        self.assertEqual(ns.x, 1)
        self.assertEqual(ns.y, 2)
        self.assertEqual(ns.w, 3)
        with self.assertRaises(AttributeError):
            ns.z

    def test_attrset(self):
        ns = Namespace(x=1, y=2, w=3)
        ns.z = 4

        self.assertEqual(sorted(ns.__dict__.items()),
                         [('w', 3), ('x', 1), ('y', 2), ('z', 4)])

    def test_eq(self):
        pass

    def test_ne(self):
        pass

    def test_repr(self):
        ns1 = Namespace(x=1, y=2, w=3)
        ns2 = Namespace()
        ns2.x = "spam"
        ns2._y = 5

        self.assertEqual(repr(ns1), "Namespace(w=3, x=1, y=2)")
        self.assertEqual(repr(ns2), "Namespace(x='spam', _y=5)")
