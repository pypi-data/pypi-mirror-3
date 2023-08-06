"""namespace module

You can think of every object in Python as a namespace (in essense, a
mapping).  The namespace of an object is exposed by its __dir__()
special method, which amounts to a "namespace protocol".

Some objects also represent namespaces.  This includes mappings (like
dict), sequences (like list or str), modules, and classes.

Sometimes you just want a namespace without all the normal object
attributes getting in the way.  This module aims to provide that.

The Namespace class is a dict subclass that exposes its keys as
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
>>> spam['x'] = 2
>>> spam['x']
2

>>> spam = as_namespace({'x': 1, 'y': 2})
>>> spam
Namespace({'x': 1, 'y': 2})

>>> class spam:
...     x = 1
...     y = 2
...
>>> spam = as_namespace(spam)
>>> spam
Namespace({'x': 1, 'y': 2})

>>> @as_namespace
... class spam:
...     x = 1
...     y = 2
...
>>> spam
Namespace({'x': 1, 'y': 2})

>>> spam.pop('x')
Traceback (most recent call last):
  ...
AttributeError: type object 'Namespace' has no attribute 'pop'

To Do:
 - make an ImmutableNamespace class

"""

from collections import Mapping, Sequence


class Namespace(dict):
    """A dict subclass that exposes its items as attributes.

    Some static methods are provided to make it easier to do things
    that you would normally be able to do with an object.

    Warning:  "dict(ns)" doesn't work for Namespace objects.  Instead,
    use the dict unpacking syntax: "dict(**ns)".  Even though Namespace
    is a subclass of dict, its use of __getattribute__ causes trouble.
    This is because the dict constructor will check for the attribute
    "keys" on an object to see if it is a mapping.  Otherwise it expects
    a sequence of tuples.

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
    def from_sequence(cls, obj, names=None):
        raise TypeError("Don't know how to turn a sequence into a Namespace.")

    #------------------------
    # static methods

    @staticmethod
    def getattr(obj, name):
        return object.__getattribute__(obj, name)

    @staticmethod
    def to_dict(obj):
        raise NotImplementedError
        return dict(obj)
        


class _Dummy: ...
CLASS_ATTRS = tuple(_Dummy.__dict__)
del _Dummy


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


#################################################
# test: creation

def assert_true(expr, msg=None):
    if msg is None:
        assert expr
    else:
        assert expr, msg


d = {"x": 1, "y":2}
spam1 = Namespace(d)
spam2 = Namespace.from_mapping(d)
spam3 = as_namespace(d)

try:
    as_namespace((1,2,3))
except TypeError:
    pass
else:
    assert_true(False)

class NS: x=1;y=2
spam4 = as_namespace(NS)

def f():
    return d
spam5 = as_namespace(f)

@as_namespace
class spam6: x=1;y=2

@as_namespace
def spam7():
    return d

class X:
    def __init__(self, x, y):
        self.x = x
        self.y = y
spam8 = as_namespace(X(1,2))
spam9 = as_namespace(X(1,2), ("x", "y"))

        
#################################################
# test access

for i in range(9):
    i += 1
    name = "spam%s" % i
    ns = globals()[name]
    print(name)
    print(ns)
    
    # test all
    assert_true(isinstance(ns, Namespace), name)

    if i in (8,):
        continue
    # test some
    assert_true(dir(ns) == sorted(dict.keys(ns)), name)
    assert_true(dict(**ns) == d, name)

assert_true(spam1.x == spam1["x"] == d["x"])

try:
    spam1.pop
    spam1.__getattribute__
except AttributeError:
    pass
else:
    assert_true(False)

#################################################
# test mutability

spam1.x = 5
assert_true(spam1.x == spam["x"] == 5)
spam1['x'] = 1
assert_true(spam1.x == spam["x"] == 1)

