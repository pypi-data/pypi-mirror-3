# -*- coding: utf-8 -*-
'''stuf deep object utilities'''

from operator import itemgetter, attrgetter, getitem

from stuf.six import get_ident, items


def attr_or_item(this, key):
    '''
    Get attribute or item.

    :argument this: an object
    :argument key: key to lookup
    '''
    try:
        return getitem(this, key)
    except KeyError:
        return getter(this, key)


def clsname(this):
    '''
    Get class name.

    :argument this: an object
    '''
    return getattr(this.__class__, '__name__')


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


def getcls(this):
    '''
    Get class of instance.

    :argument this: an instance
    '''
    return getter(this, '__class__')


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


def getdefault(this, key, default=None):
    '''
    Get an attribute.

    :argument this: an object
    :argument str key: key to lookup
    :keyword default: default value returned if key not found
    '''
    return getter(this, key, default)


get_or_default = getdefault


def instance_or_class(key, this, that):
    '''
    Get attribute of an instance or class.

    :argument str key: name of attribute to look for
    :argument this: instance to check for attribute
    :argument that: class to check for attribute
    '''
    try:
        return getter(this, key)
    except AttributeError:
        return getter(that, key)


def inverse_lookup(value, this, default=None):
    '''
    Get attribute of an instance by value.

    :argument value: value to lookup as a key
    :argument this: instance to check for attribute
    :keyword default: default key (default: None)
    '''
    try:
        return itemgetter(value)(
            dict((v, k) for k, v in items(vars(this)))
        )
    except (TypeError, KeyError):
        return default


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


def selfname(this):
    '''
    Get object name.

    :argument this: an object
    '''
    return getter(this, '__name__')


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
