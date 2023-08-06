# -*- coding: utf-8 -*-
'''stuf utilities'''

from threading import Lock
from itertools import starmap
from collections import Iterable
from importlib import import_module
from functools import update_wrapper
from operator import itemgetter, attrgetter, getitem

from stuf.six import items, get_ident, map, isstring


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


def lazyimport(path, attribute=None, i=import_module, g=getattr, s=isstring):
    '''
    deferred module loader

    :argument path: something to load
    :keyword str attribute: attribute on loaded module to return
    '''
    if s(path):
        try:
            dot = path.rindex('.')
            # import module
            path = g(i(path[:dot]), path[dot + 1:])
        # If nothing but module name, import the module
        except (AttributeError, ValueError):
            path = i(path)
        if attribute:
            path = g(path, attribute)
    return path


def lru(maxsize=100):
    '''
    Least-recently-used cache decorator.

    If *maxsize* is set to None, the LRU features are disabled and the cache
    can grow without bound.

    Arguments to the cached function must be hashable.

    Access the underlying function with f.__wrapped__.

    See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

    By Raymond Hettinger
    '''

    # Users should only access the lru through its public API:
    #   f.__wrapped__
    # The internals of the lru are encapsulated for thread safety and
    # to allow the implementation to change (including a possible C version).

    def decorating_function(user_function):
        cache = dict()
        items_ = items
        repr_ = repr
        intern_ = intern
        # bound method to lookup key or return None
        cache_get = cache.get
        # localize the global len() function
        len_ = len
        # because linkedlist updates aren't threadsafe
        lock = Lock()
        # root of the circular doubly linked list
        root = []
        # make updateable non-locally
        nonlocal_root = [root]
        # initialize by pointing to self
        root[:] = [root, root, None, None]
        # names for the link fields
        PREV, NEXT, KEY, RESULT = 0, 1, 2, 3

        if maxsize is None:
            def wrapper(*args, **kw):
                # simple caching without ordering or size limit
                key = repr_(args, items_(kw)) if kw else repr_(args)
                # root used here as a unique not-found sentinel
                result = cache_get(key, root)
                if result is not root:
                    return result
                result = user_function(*args, **kw)
                cache[intern_(key)] = result
                return result
        else:
            def wrapper(*args, **kw):
                # size limited caching that tracks accesses by recency
                key = repr_(args, items_(kw)) if kw else repr_(args)
                with lock:
                    link = cache_get(key)
                    if link is not None:
                        # record recent use of the key by moving it to the
                        # front of the list
                        root, = nonlocal_root
                        link_prev, link_next, key, result = link
                        link_prev[NEXT] = link_next
                        link_next[PREV] = link_prev
                        last = root[PREV]
                        last[NEXT] = root[PREV] = link
                        link[PREV] = last
                        link[NEXT] = root
                        return result
                result = user_function(*args, **kw)
                with lock:
                    root = nonlocal_root[0]
                    if len_(cache) < maxsize:
                        # put result in a new link at the front of the list
                        last = root[PREV]
                        link = [last, root, key, result]
                        cache[intern_(key)] = last[NEXT] = root[PREV] = link
                    else:
                        # use root to store the new key and result
                        root[KEY] = key
                        root[RESULT] = result
                        cache[intern_(key)] = root
                        # empty the oldest link and make it the new root
                        root = nonlocal_root[0] = root[NEXT]
                        del cache[root[KEY]]
                        root[KEY] = None
                        root[RESULT] = None
                return result

        wrapper.__wrapped__ = user_function
        return update_wrapper(wrapper, user_function)

    return decorating_function


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
