# -*- coding: utf-8 -*-
'''stuf deep object utilities'''

from functools import partial
from operator import attrgetter, getitem

from stuf.six import get_ident

clsdict = attrgetter('__dict__')
selfname = attrgetter('__name__')
# Get class of instance.
getcls = attrgetter('__class__')
clsname = lambda this: selfname(getcls(this))

# lightweight object manipulation
hasit = lambda x, y: y in clsdict(x)
getit = lambda x, y: clsdict(x)[y]
setit = lambda x, y, z: clsdict(x).__setitem__(y, z)
delit = lambda x, y: clsdict(x).__delitem__(y)


def attr_or_item(this, key):
    '''
    Get attribute or item.

    :argument this: an object
    :argument key: key to lookup
    '''
    try:
        return getitem(this, key)
    except (KeyError, TypeError):
        return getter(this, key)


def deepget(this, key, default=None):
    '''
    Get an attribute with deep attribute path

    :argument this: an object
    :argument str key: key to lookup
    :keyword default: default value returned if key not found
    '''
    try:
        return attrgetter(key)(this)
    except AttributeError:
        return default


def deleter(this, key):
    '''
    Delete an attribute.

    :argument this: an object
    :argument str key: key to lookup
    '''
    try:
        object.__delattr__(this, key)
    except (TypeError, AttributeError):
        delattr(this, key)


def getter(this, key):
    '''
    Get an attribute.

    :argument this: an object
    :argument str key: key to lookup
    '''
    try:
        return object.__getattribute__(this, key)
    except (AttributeError, TypeError):
        return getattr(this, key)


def members(this):
    '''
    Iterator version of ``inspect.getmembers``.
    '''
    getr = partial(getattr, this)
    for key in dir(this):
        try:
            value = getr(key)
        except AttributeError:
            pass
        else:
            yield key, value


def recursive_repr(this):
    '''
    Decorator to make a repr function return "..." for a recursive call.

    :argument this: an object
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


def setter(this, key, value):
    '''
    Set attribute.

    :argument this: an object
    :argument key: key to set
    :argument value: value to set
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
    Get an attribute, creating and setting it if needed

    :argument this: an object
    :argument key: key to lookup
    :argument default: default value returned if key not found
    '''
    try:
        return getter(this, key)
    except AttributeError:
        return setter(this, key, default)
