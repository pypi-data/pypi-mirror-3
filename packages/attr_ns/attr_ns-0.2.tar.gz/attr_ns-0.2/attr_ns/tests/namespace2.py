"""namespace module

Every object in python has a namespace, the mapping of attributes to
values for that object.  The namespace of an object is exposed by its
__dir__() special method, effectively an "object namespace protocol".

Some objects also represent separate namespaces.  This includes
mappings (like dict), sequences (like list or str), modules, and
classes.

Sometimes you just want a namespace without all the normal object
attributes getting in the way.  This module aims to provide that.

The Namespace class here is a dict subclass that exposes its keys as
attributes.  The as_namespace() function converts an object into a new
Namespace object.  It may be used as a function or class decorator.

Example:

>>> spam = {'x': 1, 'y': 2}
>>> spam = Namespace(spam)
>>> spam
Namespace({'x': 1, 'y': 2})
>>> dir(spam)
['x', 'y']
>>> spam.x
1
>>> spam.x = 3
>>> spam.x
3

>>> @as_namespace
... class spam:
...     x = 1
...     y = 2
...
>>> spam
Namespace({'x': 1, 'y': 2})

"""

__all__ = ("Namespace", "as_namespace")


from collections import Mapping, Sequence


class _Dummy: ...
CLASS_ATTRS = dir(_Dummy)
del _Dummy


class Namespace(dict):
    """A dict subclass that exposes its items as attributes.

    Even though Namespace is a subclass of dict, none of dict's instance
    attributes are available on Namespace objects.  This is due to the
    use of __getattribute__().  This does not impact the use of special
    methods by operators and builtins since those looked-up on the class
    and not the instance.

    Just to clarify, here are the methods you might normally use on a
    dict instance that are not available on Namespace instances:

      clear, copy, fromkeys, get, items, keys, pop, popitem,
      setdefault, update, values

    The special methods are likewise hidden.  You can look them any of
    the attributes on the class to access them:

        dict.copy(ns)
        type(ns).copy(ns)
        Namespace.__getitem__(ns, "x")

    Also, the Namespace class has some static methods to make it easier
    to do things that you would normally be able to do with an object.

    Warning:  "dict(ns)" doesn't work for Namespace objects.  Instead,
    use the dict unpacking syntax: "dict(**ns)".  The dict constructor
    looks for the "keys" attribute on the passed object to see if it is
    a mapping (__getattribute__() precludes that here).

    """

    def __init__(self, obj={}):
        super().__init__(obj)

    def __dir__(self):
        return tuple(self)

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, super().__repr__())

    def __getattribute__(self, name):
        try:
            return self[name]
        except KeyError:
            msg = "'%s' object has no attribute '%s'"
            raise AttributeError(msg % (type(self).__name__, name))

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    #------------------------
    # "copy constructors"

    @classmethod
    def from_object(cls, obj, names=None):
        if names is None:
            names = dir(obj)
        ns = {name:getattr(obj, name) for name in names}
        return cls(ns)

    @classmethod
    def from_mapping(cls, ns, names=None):
        if names:
            ns = {name:ns[name] for name in names}
        return cls(ns)

    @classmethod
    def from_sequence(cls, seq, names=None):
        if names:
            seq = {name:val for name, val in seq if name in names}
        return cls(seq)

    #------------------------
    # static methods

    @staticmethod
    def hasattr(ns, name):
        try:
            object.__getattribute__(ns, name)
        except AttributeError:
            return False
        return True

    @staticmethod
    def getattr(ns, name):
        return object.__getattribute__(ns, name)

    @staticmethod
    def setattr(ns, name, value):
        return object.__setattr__(ns, name, value)

    @staticmethod
    def delattr(ns, name):
        return object.__delattr__(ns, name)


def as_namespace(obj, names=None):

    # functions
    if isinstance(obj, type(as_namespace)):
        obj = obj()

    # special cases
    if isinstance(obj, type):
        names = (name for name in dir(obj) if name not in CLASS_ATTRS)
        return Namespace.from_object(obj, names)
    if isinstance(obj, Mapping):
        return Namespace.from_mapping(obj, names)
    if isinstance(obj, Sequence):
        return Namespace.from_sequence(obj, names)
    
    # default
    return Namespace.from_object(obj, names)


class FrozenNamespace(Namespace):
    """A frozen Namespace.

    Based on http://code.activestate.com/recipes/414283/.

    """

    @property
    def _blocked_attribute(obj):
        raise AttributeError("A frozendict cannot be modified.")
    __delitem__ = __setitem__ = clear = _blocked_attribute
    pop = popitem = setdefault = update = _blocked_attribute
    __delattr__ = __setattr__ = _blocked_attribute

    def __new__(cls, *args, **kwargs):
        obj = dict.__new__(cls)
        dict.__init__(obj, *args, **kwargs)
        return obj 

    def __init__(self, *args):
        pass

    def __hash__(self):
        try:
            return self._cached_hash
        except AttributeError:
            h = self._cached_hash = hash(frozenset(self.items()))
            return h

    def __repr__(self):
        return "frozendict({})".format(dict.__repr__(self))

