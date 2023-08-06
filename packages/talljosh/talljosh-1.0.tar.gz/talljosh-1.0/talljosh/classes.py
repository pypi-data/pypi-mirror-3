import functools
import UserDict

class FunctionMeta(type):
    '''
    Metaclass for Functions. Ensures that Functions can be used as methods in
    classes.
    '''
    def __get__(self, instance, class_):
        if instance is None:
            return self
        return functools.partial(self, instance)

class Function(object):
    '''
    Superclass for defining extensible functions, potentially having related
    helper functions. When the class is called, its run() method is used as the
    entrypoint.

    This is useful for defining extensible patterns of instructions.

    e.g.

    >>> class doSomething(Function):
    >>>     someConst = 17
    >>>     def run(self, value):
    >>>         self.value = value
    >>>         x = self.getX()
    >>>         return x + self.someConst

    >>>     def getX(self):
    >>>         return self.value

    >>> doSomething(13)
    30
    '''
    __metaclass__ = FunctionMeta
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls).run(*args, **kwargs)

class CallbackSet(object):
    '''
    A set that calls the given functions whenever anything is added to or
    removed from the set.
    '''
    def __init__(self, on_add, on_remove):
        self.on_add = on_add
        self.on_remove = on_remove
        self.data = set()

    def add(self, item):
        self.data.add(item)
        self.on_add(item)

    def clear(self):
        while self.data:
            self.pop()

    def discard(self, item):
        try:
            self.remove(item)
        except KeyError:
            pass

    def pop(self):
        item = self.data.pop()
        self.on_remove(item)

    def remove(self, item):
        self.data.remove(item)
        self.on_remove(item)

    def update(self, items):
        for item in items:
            self.add(item)

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return '{}<{}>'.format(self.__class__.__name__, sorted(self.data))

class MultiMap(UserDict.IterableUserDict):
    '''
    A many-to-many mapping.
    self.reverse is the reverse mapping, and is updated to keep both MultiMaps
    in synchronisation with one another.
    '''

    def __init__(self, initial_data=None, reverse=None):
        UserDict.IterableUserDict.__init__(self)
        if reverse is None:
            reverse = self.__class__(reverse=self)
        self.reverse = reverse

        if initial_data:
            for k, values in dict(initial_data).iteritems():
                self[k] = values

    def __hash__(self):
        raise TypeError('unhashable type: {!r}'.format(self.__class__.__name__))

    def construct_values_set(self, key):
        return CallbackSet(
                on_add=functools.partial(self.item_added, key),
                on_remove=functools.partial(self.item_removed, key))

    def __setitem__(self, key, values):
        values_list = self.data.setdefault(key, self.construct_values_set(key))

        if values is values_list:
            return

        values = iter(values)
        values_list.clear()
        values_list.update(values)

    def __delitem__(self, key):
        self.data[key].clear()
        del self.data[key]

    def item_added(self, key, value):
        keys_list = self.reverse.data.setdefault(value, self.reverse.construct_values_set(value))
        keys_list.data.add(key)

    def item_removed(self, key, value):
        self.reverse[value].data.remove(key)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.data)

    def setdefault(self, key, default=None):
        if not default:
            default = []
        return UserDict.IterableUserDict.setdefault(self, key, default)

    def get(self, key, default=None):
        if not default:
            default = []
        return UserDict.IterableUserDict.get(self, key, default)
