# -*- coding: utf-8 -*-
'''core stuf'''

from itertools import starmap
from collections import Mapping, Sequence, defaultdict, namedtuple

from stuf.six import items, keys, values
from stuf.utils import OrderedDict, getter, imap
from stuf.base import directstuf, wrapstuf, writewrapstuf

__all__ = ('defaultstuf', 'fixedstuf', 'frozenstuf', 'orderedstuf', 'stuf')


class defaultstuf(directstuf, defaultdict):

    '''
    dictionary with attribute-style access and a factory function to provide a
    default value for keys with no value
    '''

    _map = defaultdict

    def __getattr__(self, key):
        try:
            if key == 'iteritems':
                return items(self)
            elif key == 'iterkeys':
                return keys(self)
            elif key == 'itervalues':
                return values(self)
            return object.__getattribute__(self, key)
        except AttributeError:
            return self[key]

    def __init__(self, default, *args, **kw):
        '''
        @param default: function that can provide default values
        @param *args: iterable of keys/value pairs
        @param **kw: keyword arguments
        '''
        defaultdict.__init__(self, default)
        directstuf.__init__(self, *args, **kw)

    @classmethod
    def _build(cls, default, iterable, _map=imap, _list=list):
        kind = cls._map
        # add class to handle potential nested objects of the same class
        kw = kind(default)
        update = kw.update
        if isinstance(iterable, Mapping):
            update(kind(default, iterable))
        elif isinstance(iterable, Sequence):
            # extract appropriate key-values from sequence
            def _coro(arg):
                try:
                    update(arg)
                except (ValueError, TypeError):
                    pass
            _list(_map(_coro, iterable))
        return kw

    @classmethod
    def _new(cls, default, iterable):
        return cls(default, cls._build(default, iterable))

    def _populate(self, past, future, _map=starmap, _items=items):
        def _coro(key, value, new=self._new):
            if isinstance(value, (Mapping, Sequence)):
                # see if stuf can be converted to nested stuf
                trial = new(self.default_factory, value)
                if len(trial) > 0:
                    future[key] = trial
                else:
                    future[key] = value
            else:
                future[key] = value
        list(_map(_coro, _items(past)))

    def _prepopulate(self, *args, **kw):
        kw.update(self._build(self.default_factory, args))
        return kw

    def copy(self):
        return self._build(self.default_factory, dict(self))


class fixedstuf(writewrapstuf):

    '''
    dictionary with attribute-style access with mutability restricted to
    initial keys
    '''

    def __setitem__(self, key, value):
        # only access initial keys
        if key in self.allowed:
            super(fixedstuf, self).__setitem__(key, value)
        else:
            raise KeyError('key "{0}" not allowed'.format(key))

    def __reduce__(self):
        return (self.__class__, (self._wrapped.copy(),))

    def _prepopulate(self, *args, **kw):
        iterable = super(fixedstuf, self)._prepopulate(*args, **kw)
        self.allowed = frozenset(keys(iterable))
        return iterable

    def popitem(self):
        raise AttributeError()

    def pop(self, key, default=None):
        raise AttributeError()


class frozenstuf(wrapstuf, Mapping):

    '''immutable dictionary with attribute-style access'''

    __slots__ = ['_wrapped']

    def __getitem__(self, key):
        try:
            return getattr(self._wrapped, key)
        except AttributeError:
            raise KeyError('key {0} not found'.format(key))

    def __iter__(self, _iter=iter, _getr=getter):
        return _iter(_getr(self, '_wrapped')._asdict())

    def __len__(self, _len=len, _getr=getter):
        return _len(getter(self, '_wrapped')._asdict())

    def __reduce__(self, _getter=getter):
        return (self.__class__, (_getter(self, '_wrapped')._asdict().copy(),))

    @classmethod
    def _mapping(self, mapping, _namedtuple=namedtuple, _keys=keys):
        return _namedtuple('frozenstuf', _keys(mapping))(**mapping)


class orderedstuf(writewrapstuf):

    '''dictionary with dot attributes that remembers insertion order'''

    _mapping = OrderedDict

    def __reversed__(self):
        return getter(self, '_wrapped').__reversed__()

    def __reduce__(self):
        return self._wrapped.__reduce__()


class stuf(directstuf, dict):

    '''dictionary with attribute-style access'''
