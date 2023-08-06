# -*- coding: utf-8 -*-
'''core stuf'''

from itertools import chain
from operator import methodcaller
from collections import (
    Mapping, MutableMapping, Sequence, defaultdict, namedtuple)

from stuf.desc import lazy
from stuf.collects import OrderedDict
from stuf.iterable import exhaust, exhaustmap
from stuf.deep import recursive_repr, clsname, getcls
from stuf.six import items, strings, map, getvalues, getitems, getkeys

__all__ = 'defaultstuf fixedstuf frozenstuf orderedstuf stuf'.split()


class corestuf(object):

    '''stuf core stuff'''

    _map = dict
    _reserved = ('allowed', '_wrapped', '_map')

    def __getattr__(self, key, _getter=object.__getattribute__):
        if key == 'iteritems':
            return getitems(self)
        elif key == 'iterkeys':
            return getkeys(self)
        elif key == 'itervalues':
            return getvalues(self)
        try:
            return self[key]
        except KeyError:
            return _getter(self, key)

    @recursive_repr
    def __repr__(self):
        return '{0}({1})'.format(clsname(self), methodcaller('items')(self))

    @lazy
    def _classkeys(self):
        # protected keywords
        return frozenset(chain(
            iter(vars(self)), iter(vars(getcls(self))), self._reserved,
        ))

    @classmethod
    def _build(cls, iterable):
        kind = cls._map
        # add class to handle potential nested objects of the same class
        kw = kind()
        update = kw.update
        if isinstance(iterable, Mapping):
            update(kind(items(iterable)))
        elif isinstance(iterable, Sequence):
            # extract appropriate key-values from sequence
            def _coro(arg, update=update):
                try:
                    update(arg)
                except (ValueError, TypeError):
                    pass
            exhaust(map(_coro, iterable))
        return kw

    @classmethod
    def _mapping(cls, iterable):
        return cls._map(iterable)

    @classmethod
    def _new(cls, iterable):
        return cls(cls._build(iterable))

    @classmethod
    def _populate(cls, past, future, _is=isinstance):
        def _coro(key, value, new=cls._new, _is=_is):
            if _is(value, (Sequence, Mapping)) and not _is(value, strings):
                # see if stuf can be converted to nested stuf
                trial = new(value)
                future[key] = trial if len(trial) > 0 else value
            else:
                future[key] = value
        exhaustmap(past, _coro)
        return cls._postpopulate(future)

    @classmethod
    def _postpopulate(cls, future):
        return future

    def _prepopulate(self, *args, **kw):
        kw.update(self._build(args))
        return kw

    def copy(self):
        return self._new(self._map(self))


class writestuf(corestuf):

    def __setattr__(self, key, value):
        # handle normal object attributes
        if key == '_classkeys' or key in self._classkeys:
            self.__dict__[key] = value
        # handle special attributes
        else:
            try:
                self[key] = value
            except KeyError:
                raise AttributeError(key)

    def __delattr__(self, key):
        # allow deletion of key-value pairs only
        if not key == '_classkeys' or key in self._classkeys:
            try:
                del self[key]
            except KeyError:
                raise AttributeError(key)

    def update(self, *args, **kw):
        self._populate(self._prepopulate(*args, **kw), self)


class directstuf(writestuf):

    __init__ = writestuf.update


class wrapstuf(corestuf):

    def __init__(self, *args, **kw):
        '''
        :param *args: iterable of keys/value pairs
        :param **kw: keyword arguments
        '''
        super(wrapstuf, self).__init__()
        self._wrapped = self._populate(
            self._prepopulate(*args, **kw), self._map(),
        )

    @classmethod
    def _postpopulate(cls, future):
        return cls._mapping(future)


class writewrapstuf(wrapstuf, writestuf, MutableMapping):

    '''Wraps mappings for stuf.'''

    def __getitem__(self, key):
        return self._wrapped[key]

    def __setitem__(self, key, value):
        self._wrapped[key] = value

    def __delitem__(self, key):
        del self._wrapped[key]

    def __iter__(self):
        return iter(self._wrapped)

    def __len__(self):
        return len(self._wrapped)

    def clear(self):
        self._wrapped.clear()

    def __reduce__(self):
        return (getcls(self), (self._wrapped.copy(),))


class defaultstuf(directstuf, defaultdict):

    '''
    Dictionary with attribute-style access and a factory function to provide a
    default value for keys with no value.
    '''

    _map = defaultdict

    def __init__(self, default, *args, **kw):
        '''
        :argument default: function that can provide default values
        :param *args: iterable of keys/value pairs
        :param **kw: keyword arguments
        '''
        defaultdict.__init__(self, default)
        directstuf.__init__(self, *args, **kw)

    @classmethod
    def _build(cls, default, iterable):
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
            exhaust(map(_coro, iterable))
        return kw

    @classmethod
    def _new(cls, default, iterable):
        return cls(default, cls._build(default, iterable))

    def _populate(self, past, future):
        def _coro(key, value, new=self._new):
            if isinstance(value, (Mapping, Sequence)):
                # see if stuf can be converted to nested stuf
                trial = new(self.default_factory, value)
                future[key] = trial if len(trial) > 0 else value
            else:
                future[key] = value
        exhaustmap(past, _coro)

    def _prepopulate(self, *args, **kw):
        kw.update(self._build(self.default_factory, args))
        return kw

    def copy(self):
        return self._new(self.default_factory, dict(self))


class fixedstuf(writewrapstuf):

    '''
    Dictionary with attribute-style access where mutability is restricted to
    initial keys.
    '''

    def __setitem__(self, key, value):
        # only access initial keys
        if key in self.allowed:
            super(fixedstuf, self).__setitem__(key, value)
        else:
            raise KeyError('key "{0}" not allowed'.format(key))

    def _prepopulate(self, *args, **kw):
        iterable = super(fixedstuf, self)._prepopulate(*args, **kw)
        self.allowed = frozenset(iterable)
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

    def __iter__(self):
        return iter(self._wrapped._asdict())

    def __len__(self):
        return len(self._wrapped._asdict())

    def __reduce__(self):
        return (getcls(self), (self._wrapped._asdict().copy(),))

    @classmethod
    def _mapping(self, mapping):
        return namedtuple('frozenstuf', iter(mapping))(**mapping)


class orderedstuf(writewrapstuf):

    '''dictionary with dot attributes that remembers insertion order'''

    _mapping = OrderedDict

    def __reversed__(self):
        return self._wrapped.__reversed__()


class stuf(directstuf, dict):

    '''dictionary with attribute-style access'''
