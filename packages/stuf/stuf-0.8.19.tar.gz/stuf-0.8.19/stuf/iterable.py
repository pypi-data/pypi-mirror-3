# -*- coding: utf-8 -*-
'''stuf iterable helpers'''

from itertools import starmap

from stuf.six import items, map


def breakcount(func, length):
    '''
    Run an iterator until it reaches its original length.

    :param iterable: an iterable to exhaust
    '''
    while length:
        yield func()
        length -= 1


def count(iterable, enumerate=enumerate, next=next, S=StopIteration):
    '''Lazily calculate number of items in `iterable`.'''
    counter = enumerate(iterable, 1)
    idx = ()
    while 1:
        try:
            idx = next(counter)
        except S:
            try:
                return next(idx.__iter__())
            except S:
                return 0


def deferfunc(func):
    '''Defer running `func`.'''
    yield func()


def deferiter(iterator):
    '''Defer running `iterator`.'''
    yield next(iterator)


def exhaust(iterable, exception=StopIteration, _n=next):
    '''
    Call next on an iterator until it's exhausted.

    :param iterable: an iterable to exhaust
    :param exception: exception that marks end of iteration
    '''
    try:
        while 1:
            _n(iterable)
    except exception:
        pass


def exhaustmap(mapping, call, filter=None, exception=StopIteration, _n=next):
    '''
    Call `next` on an iterator until it's exhausted.

    :param mapping: a mapping to exhaust
    :param call: call to handle what survives the filter
    :param filter: a filter to apply to mapping
    :param exception: exception sentinel
    '''
    iterable = starmap(
        call,
        filter(filter, items(mapping)) if
        filter is not None else items(mapping),
    )
    try:
        while 1:
            _n(iterable)
    except exception:
        pass


def exhaustcall(call, iterable, exception=StopIteration, _n=next, map=map):
    '''
    Call function on an iterator until it's exhausted.

    :param call: call that does the exhausting
    :param iterable: iterable to exhaust
    :param exception: exception marking end of iteration
    '''
    iterable = map(call, iterable)
    try:
        while 1:
            _n(iterable)
    except exception:
        pass


def iterexcept(func, exception, start=None):
    '''
    Call a function repeatedly until an exception is raised.

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
