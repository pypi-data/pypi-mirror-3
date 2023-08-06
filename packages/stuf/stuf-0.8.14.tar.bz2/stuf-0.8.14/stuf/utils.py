# -*- coding: utf-8 -*-
'''stuf utilities'''

from itertools import starmap
from collections import Iterable

from functools import wraps, update_wrapper
from operator import itemgetter, attrgetter, getitem

from stuf.six import OrderedDict, items, get_ident, map, isstring


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


def exhaust(iterable, exception=StopIteration, _n=next):
    '''
    call next on an iterator until it's exhausted

    @param iterable: an iterable to exhaust
    @param exception: exception that marks end of iteration
    '''
    try:
        while True:
            _n(iterable)
    except exception:
        pass


def breakcount(func, length):
    '''
    run an iterator until it reaches its original length

    @param iterable: an iterable to exhaust
    '''
    while length:
        yield func()
        length -= 1


def exhaustmap(mapping, call, filter=False, exception=StopIteration, _n=next):
    '''
    call `next` on an iterator until it's exhausted

    @param mapping: a mapping to exhaust
    @param call: call to handle what survives the filter
    @param filter: a filter to apply to mapping (default: `None`)
    @param exception: exception sentinel (default: `StopIteration`)
    '''
    subiter = filter(filter, items(mapping)) if filter else items(mapping)
    iterable = starmap(call, subiter)
    try:
        while True:
            _n(iterable)
    except exception:
        pass


def exhaustcall(call, iterable, exception=StopIteration, _n=next):
    '''
    call function on an iterator until it's exhausted

    @param call: call that does the exhausting
    @param iterable: iterable to exhaust
    @param exception: exception marking end of iteration
    '''
    iterable = map(call, iterable)
    try:
        while True:
            _n(iterable)
    except exception:
        pass


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


def iterexcept(func, exception, start=None):
    '''
    call a function repeatedly until an exception is raised

    Converts a call-until-exception interface to an iterator interface. Like
    `__builtin__.iter(func, sentinel)` but uses an exception instead of a
    sentinel to end the loop.

    Raymond Hettinger Python Cookbook recipe # 577155
    '''
    try:
        if start is not None:
            yield start()
        while 1:
            yield func()
    except exception:
        pass


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


def deferfunc(func):
    yield func()


def deferiter(iterz):
    yield next(iterz)


def deferyield(iterz):
    yield iterz


def iterthing(iterator, wrapper, noniter):
    yield wrapper(iterator(wrapper(noniter)))


def makeiter(wrapper, thing):
    if not isstring(thing) and isinstance(thing, Iterable):
        return thing
    return wrapper(thing)

lru_wrapped = lru
get_or_default = getdefault


lru_wrapped = lru
get_or_default = getdefault
