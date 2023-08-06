"""Python namespaces.

This module contains various types and helper functions related to
namespaces (i.e. a mapping from names to values).  The main type is the
Namespace class, which is roughly equivalent to the
types.SimpleNamespace class.

About Namespaces
================

Namespaces are the underlying structure of Python objects.  The language
has two built-in namespace APIs: attribute-access and item-access.
Every object in Python implements the attribute-access API (described
below).  On the other hand, only some objects (like dicts) implement the
item-access protocol.  Such types do so to allow interacting with an
additional namespace, contained by the object.

You can think of every object in Python as having a namespace that you
access through its attributes.  That *may* map directly to the object's
__dict__, which it typically does for non-builtin types, but that's by
no means guaranteed.  For instance, some objects do not expose __dict__.
Others expose it but only as a read-only wrapper around the underlying
namespace.  And even if an object has a __dict__, it may not represent
the object's full namespace.

The base object type falls into the category of types that expose only a
read-only namespace.  So, using a direct instance of object as a
quick-and-dirty attribute-based namespace doesn't work.  This is exactly
the motivation for a simple namespace type.

You might wonder why attribute access is such a big deal that a dict
isn't sufficient.  While some might argue that attribute access requires
3 fewer characters per access, that is not the major reason.  Rather,
the main value lies in what visual inspection of the code conveys:

  Item access implies impermanence to the namespace.
  Attribute access implies stability.

Kinds of Namespace
------------------

- attribute-based
- item-based
- "enum"
- "named constants"

Other Notes
-----------

A class is a special kind of attribute-based namespace that has a name
, a docstring, and methods.  Often a class's namespace is treated as
read-only.

The modules makes frequent use of LBYL when introspecting object
namespaces, since the exceptions raised by calls inside  attr lookup
would be indistinguishable from those raised by the attr lookup itself.

Bikeshedding the Name
---------------------

- record
- flexobject
- attrobject
- attrdict
- nameddict
- namedobject
- bunch


Namespace Protocols
===================

Here are the special methods and attributes that the interpreter uses
for interacting with namespaces.

Attribute-access Namespace Protocol
-----------------------------------

object.__getattribute__(name)
object.__getattr__(name)
object.__setattr__(name, value)
object.__delattr__(name)
object.__dict__
object.__dir__()

This API is used implicitly via the "." and "del" syntax, as well as the
getattr(), setattr(), delattr(), and dir() built-ins.

(also related: the descriptor protocol)

Item-access Namespace Protocol
------------------------------

object.__getitem__(key)
object.__setitem__(key, value)
object.__delitem__(key)

This API is used implicitly via the '[]' syntax.


Recipes
=======

Turn a Namespace into a dict:

  vars(ns)

Find the size of a Namespace:

  len(vars(ns))

Turn a Namespace into a class:

  type(name, (), vars(ns))

Turn an object's namespace into a Namespace object:

  Namespace(**vars(obj))
    or
  Namespace.from_object(obj)
    or
  as_namespace(obj, some_attr_list)

Create a Namespace from a sequence of pairs:

  seq = [('a', 1), ('b', 2)]
  ns = as_namespace(dict(seq), wrap=True)

Create a Namespace facade to another object:

  nsmapping = get_namespace_mapping(obj)
  ns = Namespace.wrap(nsmapping)

Use your own mapping type underneath Namespace:

  some_mapping = {}
  ro_mapping = types.MappingProxyType(some_mapping)
  ns = Namespace.wrap(ro_mapping)


References
==========

http://docs.python.org/dev/reference/datamodel.html#customizing-attribute-access
http://docs.python.org/dev/reference/datamodel.html#emulating-container-types
http://docs.python.org/dev/library/types.html#types.MappingProxyType (dictproxy)
http://docs.python.org/dev/library/types.html#types.SimpleNamespace
http://code.activestate.com/recipes/577887
http://mail.python.org/pipermail/python-ideas/2012-May/015277.html
http://docs.python.org/dev/tutorial/classes.html#odds-and-ends
http://hg.python.org/cpython/file/v3.3.0b1/Lib/argparse.py#l1177
http://hg.python.org/cpython/file/v3.3.0b1/Lib/multiprocessing/managers.py#l903

"""

__all__ = ['get_names', 'get_namespace_mapping', 'namespace_repr',
           'MappedObject', 'SimpleNamespace', 'Namespace',
           'PureNamespaceWrapper',
           'as_namedtuple',
           ]


import types
from collections import OrderedDict
from collections.abc import Mapping, MutableMapping
from reprlib import recursive_repr


CLASS_ATTRS = type("_", (), {}).__dict__.keys()


# namespace helpers

def get_names(obj, *, subset=None, public_only=False):
    """Return the names in the object's namespace.

    If subset is passed, it is used as a sequence of names to which the
    resulting list should be restricted.  If the object has a __dir__()
    method or an __all__ attribute, public_only is ignored.

    """
    # in order of priority
    if isinstance(obj, Mapping):
        names = obj.keys()
    elif hasattr(obj, '__dir__'):
        names = obj.__dir__()
        public_only = False
    elif hasattr(obj, '__all__'):
        names = obj.__all__
        public_only = False
    elif hasattr(obj, '__dict__'):
        names = obj.__dict__.keys()
    else:
        raise TypeError("cannot find object's names: {!r}".format(type(obj)))

    if public_only:
        names = [k for k in names if not k.startswith('_')]
    elif isinstance(obj, type):
        names = [k for k in names if k not in CLASS_ATTRS]

    if subset is None:
        return sorted(names)
    return sorted(k for k in names if k in subset)


def get_namespace_mapping(obj, names=None):
    """Return the mapping for the object's namespace."""
    if isinstance(obj, Mapping):
        mapping = obj
    elif hasattr(obj, "__dir__"):
        mapping = MappedObject(obj, obj.__dir__())
    elif hasattr(obj, "__dict__"):
        mapping = obj.__dict__
    else:
        raise TypeError("cannot find namespace for {!r}".format(obj))
    return mapping


def namespace_repr(obj, *, public_only=False):
    """Return the repr for the object's namespace."""
    ns = get_namespace_mapping(obj)
    if public_only:
        keys = sorted(k for k in ns if not k.startswith('_'))
    else:
        keys = sorted(ns)
    content = ("{}={!r}".format(k, ns[k]) for k in keys)
    name = getattr(obj, '__name__', type(obj).__name__)
    return "{}({})".format(name, ", ".join(content))


def get_definition_ordered_namespace(cls):
    """Return the class's namespace in the order it was executed.

    This function uses black magic, so avoid it if you can.

    """
    # DANGER!  Relies on introspection of the interpreter frame stack.
    names = get_names(cls, public_only=True)
    mapping = get_namespace_mapping(cls)
    namespace = dict((k, mapping[k]) for k in names)

    caller = inspect.current_frame().f_back
    caller_name = caller.f_globals.get('__name__')
    if not caller_name or caller_name != cls.__module__:
        raise Exception("module frame incorrect: {0}".format(caller_name))
    else:
        # the code object for the class body is one of the constants
        # on the module's code object.
        for cls_code in caller.f_code.co_consts:
            if getattr(cls_code, 'co_name', None) == cls.__name__:
                # danger: executing class body all over again...
                new_ns = OrderedDict()
                exec(cls_code, new_ns)
                keys = tuple(new_ns)
                break
        else:
            keys = tuple(namespace)

    return OrderedDict((k, namespace[k]) for k in keys if k in namespace)


# helper types

class MappedObject(MutableMapping):
    """A wrapper around an object that exposes only a pre-defined namespace.

    names must be a sequence of strings, if passed.

    """
    def __init__(self, obj, names=None):
        self.obj = obj
        self._names = names
        self._size = len(names)
    def __repr__(self):
        return ("{}({!r}, {!r})"
                ).format(type(self).__name__, self.obj, self._names)
    def __len__(self):
        if self._names is not None:
            return self._size
        return len(get_names(self.obj))
    def __iter__(self):
        if self._names is not None:
            return iter(self._names)
        return iter(get_names(self.obj))
    def __getitem__(self, key):
        names = self._names if self._names is None else get_names(self.obj)
        if key not in names or not hasattr(self.obj, key):
            raise KeyError(key)
        return getattr(self.obj, key)
    def __setitem__(self, key, value)
        names = self._names if self._names is None else get_names(self.obj)
        if key not in names:
            raise TypeError("Adding new keys not allowed ({!r}).".format(key))
        if not hasattr(self.obj, key):
            raise KeyError(key)
        setattr(self.obj, key, value)
    def __delitem__(self, key):
        names = self._names if self._names is None else get_names(self.obj)
        if key not in names:
            raise KeyError(key)
        raise TypeError("Removing keys not allowed ({!r}).".format(key))


# namespace types

SimpleNamespace = types.SimpleNamespace


class Namespace:
    """A pure-Python version of types.SimpleNamespace.

    Namespace(**kwargs)

    Also consider using as_namespace() to get a new Namespace instance.

    Examples
    ========

    >>> ns = Namespace()
    ...

    """
    @classmethod
    def metaclass(cls, *args, **kwargs):
        """A namespace subclass factory.

        If used as a "metaclass", the resultant "class" will not be a
        class at all, but rather will be an instance of a new Namespace
        subclass.  Thus passing this function as the metaclass in a
        class definition is a sneaky way of generating a namespace
        object.

        """
        if not args:
            name = cls.__name__
            bases, namespace = (), kwargs
        elif len(args) == 1:
            name, = args
            bases, namespace = (), kwargs
        elif len(args) == 2:
            name, bases = args
            namespace = kwargs
        else:
            name, bases, namespace = args
            namespace.update(kwargs)

        # create the new type
        classdict = dict((k, v)
                         for k, v in namespace.items()
                         if k in CLASS_ATTRS)
        new_class = type(name, (cls,) + bases, classdict)

        # create an instance of it
        namespacedict = dict((k, v)
                             for k, v in namespace.items()
                             if k not in CLASS_ATTRS)
        return new_class(**namespacedict)

    # XXX allow for excluded names?
    @classmethod
    def from_object(cls, obj=None, *, names=None, public_only=False):
        """Return a new namespace based on the object's namespace

        You can limit The namespace by passing a list of attribute names.

        May be used as a decorator or a decorator factory.

        """
        # handle use as decorator factory
        if obj is None:
            return lambda obj: cls.from_object(obj, names)

        names = get_names(obj, names, public_only)
        mapping = get_namespace_mapping(obj)
        ns = dict((k, mapping[k]) for k in names)
        return cls(**ns)

    @classmethod
    def wrap(cls, obj):
        """Return a namespace wrapping the object.

        Changes to the namespace are propagated to the object and vice-
        versa.

        May be used as a decorator.

        """
        ns = cls()
        if isinstance(obj, Mapping):
            ns.__dict__ = obj
        elif hasattr(obj, '__dir__'):
            ns.__dict__ = MappedObject(obj, obj.__dir__())
        else:
            ns.__dict__ = obj.__dict__
        return ns

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    @recursive_repr()
    def __repr__(self):
        return namespace_repr(self)
    def __dir__(self):
        return sorted(self.__dict__)
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return self.__dict__ != other.__dict__



# XXX what was this for, again?
class PureNamespaceWrapper:
    """An attribute-access wrapper around an object's explicit namespace.

    Normally lookup on the object's class effectively exposes a larger
    implicit namespace than the object has defined.

    """
    _objects = {}

    def __init__(self, obj, names):
        names = get_names(obj, subset=names)
        type(self)._objects[self] = (obj, names)

    def __dir__(self):
        obj, names = type(self)._objects[self]
        return names

    def __repr__(self):
        obj, names = type(self)._objects[self]
        return "{}({!r})".format(type(self).__name__, obj)

    def __getattribute__(self, name):
        obj, names = type(self)._expose_attr(self, name)
        # could go EAFP here, but will stay congruent with __init__()
        if isinstance(obj, Mapping):
            return obj[name]
        else:
            return getattr(obj, name)

    def __setattr__(self, name, value):
        obj, names = type(self)._expose_attr(self, name)
        if isinstance(obj, Mapping):
            obj[name] = value
        else:
            setattr(obj, name, value)

    def __delattr__(self, name):
        obj, names = type(self)._expose_attr(self, name)
        if isinstance(obj, Mapping):
            del obj[name]
        else:
            delattr(obj, name)

    @classmethod
    def _expose_attr(cls, instance, name):
        obj, names = cls._objects[instance]
        if name not in names:
            msg = "{!r} object has no attribute {!r}"
            raise AttributeError(msg.format(cls.__name__, name))
        return obj, names

    @classmethod
    def getattr(cls, instance, name):
        return object.__getattribute__(instance, name)


class Bunch(dict):  # attrdict
    """A mapping with attribute access.

    http://code.activestate.com/recipes/52308
    http://mail.python.org/pipermail/python-list/2002-July/162558.html
    http://code.activestate.com/recipes/577999
    https://github.com/dsc/bunch/blob/master/bunch/__init__.py
    https://github.com/makinacorpus/easydict/blob/master/easydict/__init__.py
    https://bitbucket.org/lcrees/stuf/src/e731bf353bb4/stuf/core.py

    """
    # XXX memory leak?
    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
        self.__dict__ = self
    @recursive_repr()
    def __repr__(self):
        return "{}({})".format(type(self).__name__, dict.__repr__(self))
    def __getstate__(self):
        return self
    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self


class HiddenNamespace:
    """???"""
    # XXX pull from namespace3.py


class UnlockedNamespace:
    """???"""
    # XXX pull from namespace3.py


# see freeze.py for FrozenNamespace


# related builders

def as_namedtuple(cls):
    """Convert cls to a namedtuple."""
    if cls.__bases__ and cls.__bases__ != (object,):
        raise Exception("Can't have base classes.")

    caller = sys._getframe().f_back
    namespace = get_ordered_namespace(cls, caller, public_only=True)

    newcls = namedtuple(cls.__name__, get_ordered_keys(cls, namespace))
    newcls.__annotations__ = namespace
    newcls.__doc__ = cls.__doc__
    return newcls


def as_enum(cls):
    # http://code.activestate.com/recipes/577755
    # http://code.activestate.com/recipes/577984
    raise NotImplementedError
