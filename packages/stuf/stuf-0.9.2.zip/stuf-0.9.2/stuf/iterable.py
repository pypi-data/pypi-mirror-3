# -*- coding: utf-8 -*-
'''stuf iterables.'''

from itertools import starmap

from stuf.six import items, map, next


def breakcount(call, length):
    '''Call function `call` until it reaches its original `length`.'''
    while length:
        yield call()
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
                return next(iter(idx))
            except S:
                return 0


def deferfunc(call):
    '''Defer running `call`.'''
    yield call()


def deferiter(iterator):
    '''Defer running `iterator`.'''
    yield next(iterator)


def exhaust(iterable, exception=StopIteration, _n=next):
    '''Call `next` on an `iterable` until it's exhausted.'''
    try:
        while 1:
            _n(iterable)
    except exception:
        pass


def exhaustmap(mapping, call, filter=None, exception=StopIteration, _n=next):
    '''Call `call` with optional `filter` on a `mapping` until exhausted.'''
    exhaust(starmap(
        call,
        items(mapping) if filter is None else filter(filter, items(mapping)),
    ), exception)


def exhaustcall(call, iterable, exception=StopIteration, _n=next, map=map):
    '''Call function `call` on an `iterable` until it's exhausted.'''
    exhaust(map(call, iterable), exception)


def exhauststar(call, iterable, exception=StopIteration, _n=next, map=starmap):
    '''Call function `call` on an `iterable` until it's exhausted.'''
    exhaust(map(call, iterable), exception)


def iterexcept(call, exception, start=None):
    '''
    Call function `call` repeatedly until `exception` is raised.

    from Raymond Hettinger Python Cookbook recipe # 577155
    '''
    try:
        if start is not None:
            yield start()
        while 1:
            yield call()
    except exception:
        pass
