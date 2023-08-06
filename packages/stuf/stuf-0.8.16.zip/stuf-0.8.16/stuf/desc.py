# -*- coding: utf-8 -*-
'''stuf descriptor utilities'''

from functools import update_wrapper

from stuf.deep import selfname, setter


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

    '''
    Lazily assign attributes on an instance upon first use.
    '''

    def __get__(self, this, that):
        return self if this is None else self._set(this)


class lazy_class(_lazyinit):

    '''
    Lazily assign attributes on an class upon first use.
    '''

    def __get__(self, this, that):
        return self._set(that)


class lazy_set(lazy):

    '''
    Lazily assign attributes with a custom setter.
    '''

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

    '''
    Call as both class and instance method.
    '''

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
        '''
        Modifying decorator that defines a general method.
        '''
        self.expr = expr
        return self


class both(bothbase):

    '''
    Descriptor that caches results of instance-level results while allowing
    class-level results.
    '''

    def __get__(self, this, that):
        return self.expr(that) if this is None else self._set(this)


class either(bothbase):

    '''
    Descriptor that caches results of both instance- and class-level results.
    '''

    def __get__(self, this, that):
        if this is None:
            return setter(that, self.name, self.expr(that))
        return self._set(this)


class twoway(bothbase):

    '''Descriptor that enables instance and class-level results.'''

    def __get__(self, this, that):
        return self.expr(that) if this is None else self.method(this)
