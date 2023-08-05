# -*- coding: utf-8 -*-
'''base stuf'''

from __future__ import absolute_import
from collections import Mapping, Sequence

from stuf.util import class_name, lazy, recursive_repr


class basestuf(object):

    '''stuf basestuf'''

    _mapping = dict
    _reserved = ['allowed', '_wrapped', '_mapping']

    def __init__(self, *args, **kw):
        '''
        @param *args: iterable of keys/value pairs
        @param **kw: keyword arguments
        '''
        self.update(*args, **kw)

    def __iter__(self):
        cls = self.__class__
        for k, v in self.iteritems():
            # nested stuf of some sort
            if isinstance(v, cls):
                yield (k, dict(i for i in v))
            # normal key, value pair
            else:
                yield (k, v)

    def __getattr__(self, k):
        try:
            return self.__getitem__(k)
        except KeyError:
            return object.__getattribute__(self, k)

    def __setattr__(self, k, v):
        # handle normal object attributes
        if k == '_classkeys' or k in self._classkeys:
            object.__setattr__(self, k, v)
        # handle special attributes
        else:
            try:
                self.__setitem__(k, v)
            except:
                raise AttributeError(k)

    def __delattr__(self, k):
        # allow deletion of key-value pairs only
        if not k == '_classkeys' or k in self._classkeys:
            try:
                self.__delitem__(k)
            except KeyError:
                raise AttributeError(k)

    def __getstate__(self):
        return self._mapping(self)

    @recursive_repr
    def __repr__(self):
        if not self:
            return '%s()' % class_name(self)
        return '%s(%r)' % (class_name(self), self.items())

    def __setstate__(self, state):
        return self._build(state)

    @lazy
    def _classkeys(self):
        # protected keywords
        return frozenset(
            vars(self).keys() + vars(self.__class__).keys() + self._reserved
        )

    @classmethod
    def _build(cls, iterable):
        kind = cls._mapping
        # add class to handle potential nested objects of the same class
        kw = kind()
        if isinstance(iterable, Mapping):
            kw.update(kind(i for i in iterable.items()))
        elif isinstance(iterable, Sequence):
            # extract appropriate key-values from sequence
            for arg in iterable:
                try:
                    kw.update(arg)
                except (ValueError, TypeError):
                    pass
        return kw

    @classmethod
    def _new(cls, iterable):
        return cls(cls._build(iterable))

    def _populate(self, iterable):
        new = self._new
        for k, v in iterable.iteritems():
            if isinstance(v, (Sequence, Mapping)):
                # see if stuf can be converted to nested stuf
                trial = new(v)
                if len(trial) > 0:
                    self.__setitem__(k, trial)
                else:
                    self.__setitem__(k, v)
            else:
                self.__setitem__(k, v)

    def _prepare(self, *args, **kw):
        kw.update(self._build(args))
        return kw

    def copy(self):
        return self._build(self._mapping(i for i in self))

    def update(self, *args, **kw):
        self._populate(self._prepare(*args, **kw))


class wrapstuf(basestuf):

    '''wraps mappings for stuf compliance'''

    def __getitem__(self, key):
        return self._wrapped[key]

    def __iter__(self):
        return self._wrapped.__iter__()

    def __len__(self):
        return self._wrapped.__len__()


class stuf(basestuf, dict):

    '''dictionary with attribute-style access'''
