"""Namespace stuff that isn't ready yet.

"""


CMP_SPECIAL = ('__eq__', '__ge__', '__gt__', '__le__', '__lt__', '__ne__')
DICT_SPECIAL = ('__delitem__', '__getitem__', '__setitem__',
                '__contains__', '__iter__', '__len__')
DICT_METHODS = ('clear', 'copy', 'fromkeys', 'get', 'items', 'keys',
                'pop', 'popitem', 'setdefault', 'update', 'values')
if hasattr(dict, "viewkeys"):
    DICT_METHODS += ("viewkeys", "viewvalues", "viewitems")
DICT_ATTRS = DICT_SPECIAL + CMP_SPECIAL
DICT_ALL = CMP_SPECIAL + DICT_SPECIAL + DICT_METHODS


_BORROWED = """\
def {{}}(self, *args, **kwargs):
    if hasattr(self, {!r}):
        return self.{}(*args, **kwargs)
    return object.__getattribute__(self, {!r}).{{}}(*args, **kwargs)
"""

def delegates_type(cls=None, *, name, attrs):
    """Delegate the methods in attrs from cls.name to cls."""

    # handle decorator factory
    if cls is None:
        return lambda cls: return delegates_type(cls, name, attrs)

    BORROWED = _BORROWED.format(name, name, name)
    ns = {}
    for attrname in attrs:
        exec(BORROWED.format(attrname, attrname), ns)
        setattr(cls, attrname, ns[attrname])
    return cls


@delegates_type("namespace", DICT_ATTRS)
class UnlockedNamespace(object):
    def __init__(self, ns):
        self.namespace = ns
    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, self.namespace)
    def __getattr__(self, name):
        return getattr(type(self.namespace), name)


class NamespaceMeta(type):
    def unlock(cls, ns):
        return cls.UNLOCKED_CLASS(ns)


@delegates_type("__dict__", DICT_ALL)
class Namespace(object):
    """object version"""
    __metaclass__ = NamespaceMeta
    UNLOCKED_CLASS = UnlockedNamespace
    def __init__(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, self.__dict__)
    def __getattribute__(self, name):
        dict = object.__getattribute__(self, "__dict__")
        if name == "__dict__":
            return dict
        if name not in dict:
            raise AttributeError(name)
        return dict[name]


if hasattr(dict, "viewkeys"):
    Namespace.keys = Namespace.viewkeys
    Namespace.values = Namespace.viewvalues
    Namespace.items = Namespace.viewitems



def HiddenNamespace(object):
    class __metaclass__(type): _hidden = {}

    def __init__(self, *args, **kwargs):
        type(self)._hidden[self.__name__] = Namespace()
        self.__dict__.update(*args, **kwargs)
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, self.__dict__)
    def __getattribute__(self, name):
        dict = object.__getattribute__(self, "__dict__")
        if name == "__dict__":
            return dict
        if name not in dict:
            raise AttributeError(name)
        return dict[name]

HiddenNamespace = delegates_type(HiddenNamespace, "__dict__", DICT_ALL)

if hasattr(dict, "viewkeys"):
    Namespace.keys = Namespace.viewkeys
    Namespace.values = Namespace.viewvalues
    Namespace.items = Namespace.viewitems


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


# see freeze.py for FrozenNamespace


def as_enum(cls):
    # http://code.activestate.com/recipes/577755
    # http://code.activestate.com/recipes/577984
    raise NotImplementedError


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
