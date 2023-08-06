"""another namespace module

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

