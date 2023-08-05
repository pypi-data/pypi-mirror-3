# -*- coding: utf-8 -*-
# pylint: disable-msg=w0221,w0212,w0201
'''core stuf'''

from __future__ import absolute_import
from collections import (
    MutableMapping, Mapping, Sequence, defaultdict, namedtuple,
)

from .util import OrderedDict
from .base import basestuf, wrapstuf


class defaultstuf(basestuf, defaultdict):

    '''
    dictionary with attribute-style access and a factory function to provide a
    default value for keys with no value
    '''

    _mapping = defaultdict

    def __init__(self, default, *args, **kw):
        '''
        @param default: function that can provide default values
        @param *args: iterable of keys/value pairs
        @param **kw: keyword arguments
        '''
        defaultdict.__init__(self, default)
        basestuf.__init__(self, *args, **kw)

    @classmethod
    def _build(cls, default, iterable):
        kind = cls._mapping
        # add class to handle potential nested objects of the same class
        kw = kind(default)
        if isinstance(iterable, Mapping):
            kw.update(kind(default, iterable))
        elif isinstance(iterable, Sequence):
            # extract appropriate key-values from sequence
            for arg in iterable:
                try:
                    kw.update(arg)
                except (ValueError, TypeError):
                    pass
        return kw

    @classmethod
    def _new(cls, default, iterable):
        return cls(default, cls._build(default, iterable))

    def _populate(self, iterable):
        new = self._new
        for k, v in iterable.items():
            if isinstance(v, (Mapping, Sequence)):
                # see if stuf can be converted to nested stuf
                trial = new(self.default_factory, v)
                if len(trial) > 0:
                    self[k] = trial
                else:
                    self[k] = v
            else:
                self[k] = v

    def _prepare(self, *args, **kw):
        kw.update(self._build(self.default_factory, args))
        return kw

    def copy(self):
        return self._build(self.default_factory, dict(i for i in self))

    def update(self, *args, **kw):
        self._populate(self._prepare(self.default_factory, *args, **kw))


class frozenstuf(Mapping):

    '''immutable dictionary with attribute-style access'''

    __slots__ = ['_items']

    def __init__(self, *args, **kw):
        '''
        @param *args: iterable of keys/value pairs
        @param **kw: keyword arguments
        '''
        self._items = self._populate(self._build(dict(*args, **kw)))

    def __reduce__(self):
        return self.__class__, (self._items._asdict().copy(),)

    def __getitem__(self, key):
        try:
            return getattr(self._items, key)
        except AttributeError:
            raise KeyError('key not found')

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            return getattr(self._items, key)

    def __iter__(self):
        return self._items._asdict().iterkeys()

    def __len__(self):
        return len(self._items)

    @classmethod
    def _build(cls, iterable):
        kw = dict()
        if isinstance(iterable, Mapping):
            kw.update(dict(i for i in iterable.items()))
        elif isinstance(iterable, Sequence):
            # extract appropriate key-values from sequence
            for arg in iterable:
                try:
                    kw.update(arg)
                except (ValueError, TypeError):
                    pass
        return kw

    def _freeze(self, mapping):
        frozen = namedtuple('frozenstuf', mapping.keys())
        return frozen(**mapping)

    def _populate(self, iterable):
        new = self._freeze
        for k, v in iterable.iteritems():
            if isinstance(v, basestring):
                iterable[k] = v
            elif isinstance(v, (Sequence, Mapping)):
                # see if stuf can be converted to nested stuf
                trial = frozenstuf(v)
                if len(trial) > 0:
                    iterable[k] = trial
                else:
                    iterable[k] = v
            else:
                iterable[k] = v
        return new(iterable)

    def copy(self):
        return self._build(dict(i for i in self.iteritems()))


class orderedstuf(wrapstuf, MutableMapping):

    '''dictionary with dot attributes that remembers insertion order'''

    _mapping = OrderedDict

    def __init__(self, *args, **kw):
        '''
        @param *args: iterable of keys/value pairs
        @param **kw: keyword arguments
        '''
        self._wrapped = OrderedDict()
        super(orderedstuf, self).__init__(*args, **kw)

    def __setitem__(self, key, value):
        self._wrapped[key] = value

    def __delitem__(self, key):
        del self._wrapped[key]

    def __reversed__(self):
        return self._wrapped.__reversed__()

    def __reduce__(self):
        return self._wrapped.__reduce__()

    def copy(self):
        return self._build(OrderedDict(self))


class fixedstuf(wrapstuf, MutableMapping):

    '''
    dictionary with attribute-style access with mutability restricted to
    initial keys
    '''

    def __init__(self, *args, **kw):
        '''
        @param *args: iterable of keys/value pairs
        @param **kw: keyword arguments
        '''
        self._wrapped = dict()
        super(fixedstuf, self).__init__(*args, **kw)

    def __setitem__(self, k, v):
        # only access initial keys
        if k in self.allowed:
            self._wrapped[k] = v
        else:
            raise KeyError('%s is not an allowed key' % k)

    def __setattr__(self, k, v):
        # allow normal object creation for protected keywords
        if k == '_classkeys' or k in self._classkeys:
            object.__setattr__(self, k, v)
        else:
            try:
                self[k] = v
            except KeyError:
                raise AttributeError(k)

    def __delitem__(self, key):
        self._wrapped[key] = None

    def __delattr__(self, k):
        self.__delitem__(k)

    def __reduce__(self):
        return self.__class__, (self._wrapped.copy(),)

    def _populate(self, iterable):
        self.allowed = frozenset(iterable.iterkeys())
        super(fixedstuf, self)._populate(iterable)

    def copy(self):
        return fixedstuf(self._wrapped)

    def clear(self):
        self._wrapped.clear()

    def popitem(self):
        raise AttributeError()

    def pop(self, key, default=None):
        raise AttributeError()
