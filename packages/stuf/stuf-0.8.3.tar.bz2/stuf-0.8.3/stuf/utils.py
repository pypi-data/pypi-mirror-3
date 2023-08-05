# -*- coding: utf-8 -*-
## pylint: disable-msg=w0702,f0401
'''stuf utilities'''

from __future__ import absolute_import

try:
    from collections import OrderedDict
except  ImportError:
    from ordereddict import OrderedDict
try:
    from thread import get_ident
except ImportError:
    try:
        from dummy_thread import get_ident
    except ImportError:
        from _thread import get_ident
from functools import wraps, update_wrapper
from operator import itemgetter, attrgetter, getitem


def attr_or_item(this, key):
    '''
    get attribute or item

    @param this: object
    @param key: key to lookup
    '''
    try:
        return getitem(this, key)
    except KeyError:
        return getter(this, key)


def clsname(this):
    '''
    get class name

    @param this: object
    '''
    return getattr(this.__class__, '__name__')


def deepget(this, key, default=None):
    '''
    get an attribute with deep attribute path

    @param this: object
    @param key: key to lookup
    @param default: default value returned if key not found (default: None)
    '''
    try:
        return attrgetter(key)(this)
    except AttributeError:
        return default


def deleter(this, key):
    '''
    delete an attribute

    @param this: object
    @param key: key to lookup
    '''
    try:
        object.__delattr__(this, key)
    except (TypeError, AttributeError):
        delattr(this, key)


def getcls(this):
    '''
    get class of instance

    @param this: an instance
    '''
    return getter(this, '__class__')


def getter(this, key):
    '''
    get an attribute

    @param this: object
    @param key: key to lookup
    @param default: default value returned if key not found (default: None)
    '''
    try:
        return object.__getattribute__(this, key)
    except (AttributeError, TypeError):
        return getattr(this, key)


def get_or_default(this, key, default=None):
    '''
    get an attribute

    @param this: object
    @param key: key to lookup
    @param default: default value returned if key not found (default: None)
    '''
    try:
        return getter(this, key)
    except AttributeError:
        return default


def instance_or_class(key, this, owner):
    '''
    get attribute of an instance or class

    @param key: name of attribute to look for
    @param this: instance to check for attribute
    @param owner: class to check for attribute
    '''
    try:
        return getter(this, key)
    except AttributeError:
        return getter(owner, key)


def inverse_lookup(value, this, default=None):
    '''
    get attribute of an instance by value

    @param value: value to lookup as a key
    @param this: instance to check for attribute
    @param default: default key (default: None)
    '''
    try:
        return itemgetter(value)(
            dict((v, k) for k, v in vars(this).iteritems())
        )
    except (TypeError, KeyError):
        return default


def lru_wrapped(this, maxsize=100):
    '''
    least-recently-used cache decorator from Raymond Hettinger

    arguments to the cached function must be hashable.

    @param maxsize: maximum number of results in LRU cache (default: 100)
    '''
    # order: least recent to most recent
    cache = OrderedDict()

    @wraps(this)
    def wrapper(*args, **kw):
        key = args
        if kw:
            key += tuple(sorted(kw.items()))
        try:
            result = cache.pop(key)
        except KeyError:
            result = this(*args, **kw)
            # purge least recently used cache entry
            if len(cache) >= maxsize:
                cache.popitem(0)
        # record recent use of this key
        cache[key] = result
        return result
    return wrapper


def selfname(this):
    '''
    get object name

    @param this: object
    '''
    return getter(this, '__name__')


def recursive_repr(this):
    '''
    Decorator to make a repr function return "..." for a recursive call

    @param this: object
    '''
    repr_running = set()

    def wrapper(self):
        key = id(self), get_ident()
        if key in repr_running:
            return '...'
        repr_running.add(key)
        try:
            result = this(self)
        finally:
            repr_running.discard(key)
        return result
    # Can't use functools.wraps() here because of bootstrap issues
    wrapper.__module__ = getattr(this, '__module__')
    wrapper.__doc__ = getattr(this, '__doc__')
    wrapper.__name__ = selfname(this)
    return wrapper


def setter(this, key, value):
    '''
    get an attribute

    @param this: object
    @param key: key to set
    @param value: value to set
    '''
    # it's an instance
    try:
        this.__dict__[key] = value
        return value
    # it's a class
    except TypeError:
        setattr(this, key, value)
        return value


class lazybase(object):

    '''base for lazy descriptors'''

    def __init__(self, method):
        self.method = method
        self.name = selfname(method)
        update_wrapper(self, method)


class lazy(lazybase):

    '''lazily assign attributes on an instance upon first use.'''

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return setter(instance, self.name, self.method(instance))


class lazy_class(lazybase):

    '''Lazily assign attributes on an class upon first use.'''

    def __get__(self, instance, owner):
        return setter(owner, self.name, self.method(owner))


class lazy_set(lazybase):

    '''lazy assign attributes with a custom setter'''

    def __init__(self, method, fget=None):
        super(lazy_set, self).__init__(method)
        self.fget = fget
        update_wrapper(self, method)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return setter(instance, self.name, self.method(instance))

    def __set__(self, this, value):
        self.fget(this, value)

    def __delete__(self, this):
        del this.__dict__[self.name]

    def setter(self, func):
        self.fget = func
        return self


class both(lazybase):

    '''
    decorator which allows definition of a Python descriptor with both
    instance-level and class-level behavior
    '''

    def __init__(self, method, expr=None):
        super(both, self).__init__(method)
        self.expr = expr or method
        update_wrapper(self, method)

    def __get__(self, instance, owner):
        if instance is None:
            return self.expr(owner)
        return setter(instance, self.name, self.method(instance))

    def expression(self, expr):
        '''
        a modifying decorator that defines a general method
        '''
        self.expr = expr
        return self


class either(both):

    '''
    decorator which allows caching results of a Python descriptor with both
    instance-level and class-level behavior
    '''

    def __init__(self, method, expr=None):
        super(either, self).__init__(method)
        self.expr = expr or method
        update_wrapper(self, method)

    def __get__(self, instance, owner):
        if instance is None:
            return setter(owner, self.name, self.expr(owner))
        return setter(instance, self.name, self.method(instance))

    def expression(self, expr):
        '''
        a modifying decorator that defines a general method
        '''
        self.expr = expr
        return self


__all__ = [
    'attr_or_item', 'both', 'clsname', 'deepget', 'deleter', 'either',
    'get_or_default', 'getcls', 'getter', 'instance_or_class',
    'inverse_lookup', 'lazy', 'lazy_class', 'lazy_set', 'lru_wrapped',
    'recursive_repr', 'selfname', 'setter',
]
