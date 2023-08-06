
from unittest import TestCase
from collections import OrderedDict

from namespace import (namespace_repr, namespace,
                       SimpleNamespace, Namespace, FancyNamespace)


class Test_namespace_repr(TestCase):

    def test_dict(self):
        ns = dict(a=1, c=2, b=4, _c="spam")
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "namespace(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "namespace(a=1, b=4, c=2)")

    def test_odict(self):
        ns = OrderedDict([('a', 1), ('c', 2), ('b', 4), ('_c', "spam")])
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "namespace(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "namespace(a=1, b=4, c=2)")

    def test_object(self):
        ns = type("NS", (), {})()
        ns.__dict__.update(dict(a=1, c=2, b=4, _c="spam"))
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "namespace(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "namespace(a=1, b=4, c=2)")

    def test_type(self):
        ns = type("NS", (), dict(a=1, c=2, b=4, _c="spam"))
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "namespace(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "namespace(a=1, b=4, c=2)")

    def test_namespace(self):
        ns = namespace(a=1, c=2, b=4, _c="spam")
        ns_repr = namespace_repr(ns)
        ns_repr_public = namespace_repr(ns, public_only=True)

        self.assertEqual(ns_repr, "namespace(_c='spam', a=1, b=4, c=2)")
        self.assertEqual(ns_repr_public, "namespace(a=1, b=4, c=2)")

    def test_slots(self):
        with self.assertRaises(AttributeError):
            namespace_repr(object())


class Test_namespace(TestCase):

    def test_empty(self):
        pass

    def test_name(self):
        pass

    def test_ns(self):
        pass

    def test_kwargs_only(self):
        pass

    def test_kwargs(self):
        pass

    def test_ns_plus_kwargs(self):
        pass

    def test_class_definition(self):
        pass

    def test_class_definition(self):
        pass


class TestNamespace(TestCase):

    def test_attrs(self):
        pass

    def test_dict(self):
        pass

    def test_class_definition(self):
        pass

    def test_subclass(self):
        pass

    def test_instance(self):
        pass


class TestFancyNamespace(TestCase):

    def test_dir(self):
        pass

    def test_eq(self):
        pass

    def test_ne(self):
        pass

    def test_contains(self):
        pass


class TestSimpleNamespace(TestCase):

    def test_empty(self):
        ns = SimpleNamespace()

        self.assertEqual(len(ns.__dict__), 0)

    def test_args(self):
        with self.assertRaises(TypeError):
            ns = SimpleNamespace(1)

    def test_kwargs(self):
        ns = SimpleNamespace(x=1, y=2, w=3)

        self.assertEqual(sorted(ns.__dict__.items()),
                         [('w', 3), ('x', 1), ('y', 2)])

    def test_dict(self):
        ns = SimpleNamespace(x=1, y=2, w=3)

        self.assertEqual(ns.__dict__, dict(x=1, y=2, w=3))
        self.assertEqual(vars(ns), dict(x=1, y=2, w=3))

    def test_attrget(self):
        ns = SimpleNamespace(x=1, y=2, w=3)

        self.assertEqual(ns.x, 1)
        self.assertEqual(ns.y, 2)
        self.assertEqual(ns.w, 3)
        with self.assertRaises(AttributeError):
            ns.z

    def test_attrset(self):
        ns = SimpleNamespace(x=1, y=2, w=3)
        ns.z = 4

        self.assertEqual(sorted(ns.__dict__.items()),
                         [('w', 3), ('x', 1), ('y', 2), ('z', 4)])

    def test_repr(self):
        ns1 = SimpleNamespace(x=1, y=2, w=3)
        ns2 = SimpleNamespace()
        ns2.x = "spam"
        ns2._y = 5

        self.assertEqual(repr(ns1), "SimpleNamespace(w=3, x=1, y=2)")
        self.assertEqual(repr(ns2), "SimpleNamespace(x='spam')")
