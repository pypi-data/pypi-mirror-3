# -*- coding: utf-8 -*-
'''stuf utilities'''

import re
from threading import Lock
from itertools import count
from keyword import iskeyword
from pickletools import genops
from unicodedata import normalize
from importlib import import_module
from functools import update_wrapper, partial

from stuf.six import (
    PY3, HIGHEST_PROTOCOL, items, isstring, function_code, ld, dumps, u, b,
    intern)

# count
count = partial(next, count())
# check for None
isnone = lambda x, y: x if y is None else y
# import loader
lazyload = lambda x: lazyimport(x) if isstring(x) and '.' in x else x


def diff(current, past):
    '''Difference between `past` and `current` ``dicts``.'''
    intersect = set(current).intersection(set(past))
    changed = set(o for o in intersect if past[o] != current[o])
    return dict((k, v) for k, v in items(current) if k in changed)


def lazyimport(path, attribute=None, i=import_module, g=getattr, s=isstring):
    '''
    Deferred module loader.

    :argument path: something to load
    :keyword str attribute: attribute on loaded module to return
    '''
    if s(path):
        try:
            dot = path.rindex('.')
            # import module
            path = g(i(path[:dot]), path[dot + 1:])
        # If nothing but module name, import the module
        except (AttributeError, ValueError):
            path = i(path)
        if attribute:
            path = g(path, attribute)
    return path


def lru(maxsize=100):
    '''
    Least-recently-used cache decorator.

    If *maxsize* is set to None, the LRU features are disabled and the cache
    can grow without bound.

    Arguments to the cached function must be hashable.

    Access the underlying function with f.__wrapped__.

    See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

    By Raymond Hettinger
    '''
    def decorator(user_function):
        cache = dict()
        items_ = items
        repr_ = repr
        intern_ = intern
        # bound method to lookup key or return None
        cache_get = cache.get
        # localize the global len() function
        len_ = len
        # because linkedlist updates aren't threadsafe
        lock = Lock()
        # root of the circular doubly linked list
        root = []
        # make updateable non-locally
        nonlocal_root = [root]
        # initialize by pointing to self
        root[:] = [root, root, None, None]
        # names for the link fields
        PREV, NEXT, KEY, RESULT = 0, 1, 2, 3
        if maxsize is None:
            def wrapper(*args, **kw):
                # simple caching without ordering or size limit
                key = repr_(args, items_(kw)) if kw else repr_(args)
                # root used here as a unique not-found sentinel
                result = cache_get(key, root)
                if result is not root:
                    return result
                result = user_function(*args, **kw)
                cache[intern_(key)] = result
                return result
        else:
            def wrapper(*args, **kw):
                # size limited caching that tracks accesses by recency
                key = repr_(args, items_(kw)) if kw else repr_(args)
                with lock:
                    link = cache_get(key)
                    if link is not None:
                        # record recent use of the key by moving it to the
                        # front of the list
                        root, = nonlocal_root
                        link_prev, link_next, key, result = link
                        link_prev[NEXT] = link_next
                        link_next[PREV] = link_prev
                        last = root[PREV]
                        last[NEXT] = root[PREV] = link
                        link[PREV] = last
                        link[NEXT] = root
                        return result
                result = user_function(*args, **kw)
                with lock:
                    root = nonlocal_root[0]
                    if len_(cache) < maxsize:
                        # put result in a new link at the front of the list
                        last = root[PREV]
                        link = [last, root, key, result]
                        cache[intern_(key)] = last[NEXT] = root[PREV] = link
                    else:
                        # use root to store the new key and result
                        root[KEY] = key
                        root[RESULT] = result
                        cache[intern_(key)] = root
                        # empty the oldest link and make it the new root
                        root = nonlocal_root[0] = root[NEXT]
                        del cache[root[KEY]]
                        root[KEY] = None
                        root[RESULT] = None
                return result

        def clear():
            # clear the cache and cache statistics
            with lock:
                cache.clear()
                root = nonlocal_root[0]
                root[:] = [root, root, None, None]
        wrapper.__wrapped__ = user_function
        wrapper.clear = clear
        try:
            return update_wrapper(wrapper, user_function)
        except AttributeError:
            return wrapper
    return decorator


def memoize(f, i=intern, z=items, r=repr, uw=update_wrapper):
    '''Memoize function.'''
    f.cache = {}.setdefault
    if function_code(f).co_argcount == 1:
        def memoize_(arg):
            return f.cache(i(r(arg)), f(arg))
    else:
        def memoize_(*args, **kw): #@IgnorePep8
            return f.setdefault(
                i(r(args, z(kw)) if kw else r(args)), f(*args, **kw)
            )
    return uw(f, memoize_)


if PY3:
    loads = memoize(lambda x: ld(x, encoding='latin-1'))
else:
    loads = memoize(lambda x: ld(x))


def optimize(
    obj,
    d=dumps,
    p=HIGHEST_PROTOCOL,
    s=set,
    g=genops,
    b_=b,
    n=next,
    S=StopIteration
):
    '''
    Optimize a pickle string by removing unused PUT opcodes.

    Raymond Hettinger Python cookbook recipe # 545418
    '''
    # set of args used by a GET opcode
    this = d(obj, p)
    gets = s()
    # (arg, startpos, stoppos) for the PUT opcodes
    # set to pos if previous opcode was a PUT
    def iterthing(gets=gets, this=this, g=g, n=n):  # @IgnorePep8
        gadd = gets.add
        prevpos, prevarg = None, None
        try:
            nextr = g(this)
            while 1:
                opcode, arg, pos = n(nextr)
                if prevpos is not None:
                    yield prevarg, prevpos, pos
                    prevpos = None
                if 'PUT' in opcode.name:
                    prevarg, prevpos = arg, pos
                elif 'GET' in opcode.name:
                    gadd(arg)
        except S:
            pass
    # Copy the pickle string except for PUTS without a corresponding GET
    def iterthingy(iterthing=iterthing(), this=this, n=n):  # @IgnorePep8
        i = 0
        try:
            while 1:
                arg, start, stop = n(iterthing)
                yield this[i:stop if (arg in gets) else start]
                i = stop
        except S:
            pass
        yield this[i:]
    return b_('').join(i for i in iterthingy())


class CheckName(object):

    '''Ensures string is legal Python name.'''

    # Illegal characters for Python names
    ic = '()[]{}@,:`=;+*/%&|^><\'"#\\$?!~'

    def __call__(self, name):
        ''':argument name: name to check.'''
        # Remove characters that are illegal in a Python name
        name = name.strip().lower().replace('-', '_').replace(
            '.', '_'
        ).replace(' ', '_')
        name = ''.join(i for i in name if i not in self.ic)
        # Add _ if value is a Python keyword
        return name + '_' if iskeyword(name) else name


class Sluggify(object):

    _first = staticmethod(re.compile('[^\w\s-]').sub)
    _second = staticmethod(re.compile('[-\s]+').sub)

    if PY3:
        def __call__(self, value):
            '''
            Normalizes string, converts to lowercase, removes non-alpha
            characters, and converts spaces to hyphens.
            '''
            return self._second('-', self._first(
                '', normalize('NFKD', value)
            )).strip().lower()
    else:
        def __call__(self, value):
            '''
            Normalizes string, converts to lowercase, removes non-alpha
            characters, and converts spaces to hyphens.
            '''
            return self._second('-', u(self._first(
                '', normalize('NFKD', u(value)).encode('ascii', 'ignore')
            ).strip().lower()))

lru_wrapped = lru
sluggify = Sluggify()
checkname = CheckName()
