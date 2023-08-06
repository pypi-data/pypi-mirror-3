# -*- coding: utf-8 -*-
'''stuf utilities'''

from inspect import ismodule
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

from stuf.six import items
from stuf.six.moves import filter, map  # @UnresolvedImport

imap = map
ifilter = filter


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


def getdefault(this, key, default=None):
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


def instance_or_class(key, this, that):
    '''
    get attribute of an instance or class

    @param key: name of attribute to look for
    @param this: instance to check for attribute
    @param that: class to check for attribute
    '''
    try:
        return getter(this, key)
    except AttributeError:
        return getter(that, key)


def inverse_lookup(value, this, default=None):
    '''
    get attribute of an instance by value

    @param value: value to lookup as a key
    @param this: instance to check for attribute
    @param default: default key (default: None)
    '''
    try:
        return itemgetter(value)(
            dict((v, k) for k, v in items(vars(this)))
        )
    except (TypeError, KeyError):
        return default


def lru(this, maxsize=100):
    '''
    least-recently-used cache decorator from Raymond Hettinger

    arguments to the cached function must be hashable.

    @param maxsize: maximum number of results in LRU cache (default: 100)
    '''
    # order: least recent to most recent
    cache = OrderedDict()
    @wraps(this) #@IgnorePep8
    def wrapper(*args, **kw):
        key = args
        if kw:
            key += tuple(sorted(items(kw)))
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


def recursive_repr(this):
    '''
    Decorator to make a repr function return "..." for a recursive call

    @param this: object
    '''
    repr_running = set()
    def wrapper(self): #@IgnorePep8
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


def selfname(this):
    '''
    get object name

    @param this: object
    '''
    return getter(this, '__name__')


def setter(this, key, value):
    '''
    set attribute

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


def setdefault(this, key, default=None):
    '''
    get an attribute, creating and setting it if needed

    @param this: object
    @param key: key to lookup
    @param default: default value returned if key not found (default: None)
    '''
    try:
        return getter(this, key)
    except AttributeError:
        setter(this, key, default)
        return default


class lazybase(object):

    '''base for lazy descriptors'''


class _lazyinit(lazybase):

    '''base for lazy descriptors'''

    def __init__(self, method, _wrap=update_wrapper):
        super(_lazyinit, self).__init__()
        self.method = method
        self.name = selfname(method)
        _wrap(self, method)

    def _set(self, this):
        return setter(this, self.name, self.method(this))


class lazy(_lazyinit):

    '''lazily assign attributes on an instance upon first use.'''

    def __get__(self, this, that):
        return self if this is None else self._set(this)


class lazy_class(_lazyinit):

    '''lazily assign attributes on an class upon first use.'''

    def __get__(self, this, that):
        return self._set(that)


class lazy_set(lazy):

    '''lazy assign attributes with a custom setter'''

    def __init__(self, method, fget=None, _wrap=update_wrapper):
        super(lazy_set, self).__init__(method)
        self.fget = fget
        _wrap(self, method)

    def __set__(self, this, value):
        self.fget(this, value)

    def __delete__(self, this):
        del this.__dict__[self.name]

    def setter(self, func):
        self.fget = func
        return self


class bi(_lazyinit):

    '''call as both class and instance method'''

    def __get__(self, this, that):
        return self._factory(that) if this is None else self._factory(this)

    def _factory(self, this):
        def func(*args, **kw):
            return self.method(*(this,) + args, **kw)
        setattr(this, self.name, func)
        return func


class bothbase(_lazyinit):

    def __init__(self, method, expr=None, _wrap=update_wrapper):
        super(bothbase, self).__init__(method)
        self.expr = expr or method
        _wrap(self, method)

    def expression(self, expr):
        '''modifying decorator that defines a general method'''
        self.expr = expr
        return self


class both(bothbase):

    '''
    descriptor that caches results of instance-level results while allowing
    class-level results
    '''

    def __get__(self, this, that):
        return self.expr(that) if this is None else self._set(this)


class either(bothbase):

    '''
    descriptor that caches results of both instance- and class-level results
    '''

    def __get__(self, this, that):
        if this is None:
            return setter(that, self.name, self.expr(that))
        return self._set(this)


class twoway(bothbase):

    '''descriptor that enables instance and class-level results'''

    def __get__(self, this, that):
        return self.expr(that) if this is None else self.method(this)


lru_wrapped = lru
get_or_default = getdefault

__all__ = sorted(name for name, obj in items(locals()) if not any([
    name.startswith('_'), ismodule(obj),
]))
del ismodule
