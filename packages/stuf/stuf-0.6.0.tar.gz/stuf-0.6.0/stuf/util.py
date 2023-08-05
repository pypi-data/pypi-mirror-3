# -*- coding: utf-8 -*-
## pylint: disable-msg=w0702
'''stuf utilities'''

from __future__ import absolute_import
import inspect
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident
try:
    from collections import OrderedDict
except  ImportError:
    from ordereddict import OrderedDict
from functools import wraps, update_wrapper


def class_name(this):
    '''
    get class name

    @param this: object
    '''
    return getattr(this.__class__, '__name__')


def deleter(this, key):
    '''
    delete an attribute

    @param this: object
    @param key: key to lookup
    '''
    if inspect.isclass(this):
        delattr(this, key)
    else:
        object.__delattr__(this, key)


def getter(this, key, default=None):
    '''
    get an attribute

    @param this: object
    @param key: key to lookup
    @param default: default value returned if key not found (default: None)
    '''
    if inspect.isclass(this):
        return getattr(this, key, default)
    return this.__dict__.get(key, default)


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


def object_name(this):
    '''
    get object name

    @param this: object
    '''
    return getattr(this, '__name__')


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
    wrapper.__name__ = object_name(this)
    return wrapper


def setter(this, key, value):
    '''
    get an attribute

    @param this: object
    @param key: key to set
    @param value: value to set
    '''
    if inspect.isclass(this):
        setattr(this, key, value)
    else:
        this.__dict__[key] = value


class lazybase(object):

    def __init__(self, method):
        self.method = method
        try:
            self.__doc__ = method.__doc__
            self.__module__ = method.__module__
            self.__name__ = self.name = object_name(method)
        except:
            pass


class lazy(lazybase):

    '''Lazily assign attributes on an instance upon first use.'''

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.method(instance)
        setter(instance, self.name, value)
        return value


class lazy_class(lazybase):

    '''Lazily assign attributes on an class upon first use.'''

    def __get__(self, instance, owner):
        value = self.method(owner)
        setter(owner, self.name, value)
        return value
    

class both(lazy):

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
        return super(both, self).__get__(instance, owner)

    def expression(self, expr):
        '''
        a modifying decorator that defines a general method
        '''
        self.expr = expr
        return self


class either(both):

    '''
    decorator which allows definition of a Python descriptor with both
    instance-level and class-level behavior
    '''

    def __get__(self, instance, owner):
        if instance is None:
            value = self.expr(owner)
            setter(owner, self.name, value)
            return value
        value = self.method(instance)
        setter(instance, self.name, value)
        return value
