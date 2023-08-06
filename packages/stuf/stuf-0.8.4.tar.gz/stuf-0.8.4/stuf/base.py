# -*- coding: utf-8 -*-
# pylint: disable-msg=w0231
'''base stuf'''

from itertools import chain
from operator import methodcaller
from collections import Mapping, Sequence, MutableMapping

from stuf.utils import clsname, lazy, recursive_repr


class corestuf(object):

    '''stuf core stuff'''

    _map = dict
    _reserved = ['allowed', '_wrapped', '_map']

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            if key == 'iteritems':
                return self.items
            elif key == 'iterkeys':
                return self.keys
            elif key == 'itervalues':
                return self.values
            return object.__getattribute__(self, key)

    @recursive_repr
    def __repr__(self):
        if not self:
            return '%s()' % clsname(self)
        return '%s(%r)' % (clsname(self), methodcaller('items')(self))

    @lazy
    def _classkeys(self):
        # protected keywords
        try:
            return frozenset(chain(
                vars(self).iterkeys(),
                vars(self.__class__).iterkeys(),
                self._reserved
            ))
        except AttributeError:
            return frozenset(chain(
                vars(self).keys(), vars(self.__class__).keys(), self._reserved
            ))

    @classmethod
    def _build(cls, iterable):
        kind = cls._map
        # add class to handle potential nested objects of the same class
        kw = kind()
        if isinstance(iterable, Mapping):
            try:
                iitems = iterable.iteritems
            except AttributeError:
                iitems = iterable.items
            kw.update(kind(i for i in iitems()))
        elif isinstance(iterable, Sequence):
            # extract appropriate key-values from sequence
            for arg in iterable:
                try:
                    kw.update(arg)
                except (ValueError, TypeError):
                    pass
        return kw

    @classmethod
    def _mapping(cls, iterable):
        return cls._map(iterable)

    @classmethod
    def _new(cls, iterable):
        return cls(cls._build(iterable))

    @classmethod
    def _populate(cls, past, future):
        new = cls._new
        try:
            pitems = past.iteritems
            bstring = basestring  # @UndefinedVariable
        except AttributeError:
            pitems = past.items
            bstring = str
        for key, value in pitems():
            if all([
                isinstance(value, (Sequence, Mapping)),
                not isinstance(value, bstring),
            ]):
                # see if stuf can be converted to nested stuf
                trial = new(value)
                if len(trial) > 0:
                    future[key] = trial
                else:
                    future[key] = value
            else:
                future[key] = value
        return cls._postpopulate(future)

    @classmethod
    def _postpopulate(cls, future):
        return future

    def _prepopulate(self, *args, **kw):
        kw.update(self._build(args))
        return kw

    def copy(self):
        return self._build(self._map(self))


class writestuf(corestuf):

    '''stuf basestuf'''

    def __setattr__(self, key, value):
        # handle normal object attributes
        if key == '_classkeys' or key in self._classkeys:
            self.__dict__[key] = value
        # handle special attributes
        else:
            try:
                self[key] = value
            except:
                raise AttributeError(key)

    def __delattr__(self, key):
        # allow deletion of key-value pairs only
        if not key == '_classkeys' or key in self._classkeys:
            try:
                del self[key]
            except KeyError:
                raise AttributeError(key)

    def __iter__(self):
        cls = self.__class__
        try:
            iitems = self.iteritems
        except AttributeError:
            iitems = self.items
        for key, value in iitems():
            # nested stuf of some sort
            if isinstance(value, cls):
                yield (key, dict(i for i in value))
            # normal key, value pair
            else:
                yield (key, value)

    def __getstate__(self):
        return self._mapping(self)

    def __setstate__(self, state):
        return self._build(state)

    def update(self, *args, **kw):
        self._populate(self._prepopulate(*args, **kw), self)


class directstuf(writestuf):

    '''stuf basestuf'''

    def __init__(self, *args, **kw):
        '''
        @param *args: iterable of keys/value pairs
        @param **kw: keyword arguments
        '''
        self.update(*args, **kw)


class wrapstuf(corestuf):

    def __init__(self, *args, **kw):
        '''
        @param *args: iterable of keys/value pairs
        @param **kw: keyword arguments
        '''
        super(wrapstuf, self).__init__()
        self._wrapped = self._map()
        self._wrapped = self._populate(
            self._prepopulate(*args, **kw), self._wrapped,
        )

    @classmethod
    def _postpopulate(cls, future):
        return cls._mapping(future)


class writewrapstuf(wrapstuf, writestuf, MutableMapping):

    '''wraps mappings for stuf compliance'''

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


__all__ = ['corestuf', 'directstuf', 'wrapstuf', 'writestuf', 'writewrapstuf']
