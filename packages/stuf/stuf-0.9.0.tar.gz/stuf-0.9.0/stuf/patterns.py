# -*- coding: utf-8 -*-
'''stuf search pattern utilities'''

from os import sep
from functools import partial

from stuf.utils import lru
from parse import compile as pcompile
from stuf.six.moves import filterfalse  # @UnresolvedImport
from stuf.six import isstring, filter, map, rcompile, rescape, rsub

parse = lambda expr: pcompile(expr)._search_re.search
regex = lambda expr: rcompile(expr, 32).search
glob = lambda expr: rcompile(globpattern(expr), 32).search
_SEARCH = dict(parse=parse, glob=glob, regex=regex)


def globpattern(expr):
    '''Translate glob `expr` to regular expression.'''
    i, n = 0, len(expr)
    res = []
    rappend = res.append
    while i < n:
        c = expr[i]
        i += 1
        if c == '*':
            rappend('(.*)')
        elif c == '?':
            rappend('(.)')
        elif c == '[':
            j = i
            if j < n and expr[j] == '!':
                j += 1
            if j < n and expr[j] == ']':
                j += 1
            while j < n and expr[j] != ']':
                j += 1
            if j >= n:
                rappend('\\[')
            else:
                stuff = expr[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                rappend('[{0}]'.format(stuff))
        else:
            rappend(rescape(c))
    rappend('\Z(?ms)')
    return rsub(
        r'((?<!\\)(\\\\)*)\.',
        r'\1[^{0}]'.format(r'\\\\' if sep == '\\' else sep),
        r''.join(res),
    )


@lru()
def searcher(expr):
    '''Build search function from `expr`.'''
    try:
        scheme, expr = expr.split(':', 1) if isstring(expr) else expr
        return _SEARCH[scheme](expr)
    except KeyError:
        raise TypeError('"{0}" is not a valid search scheme'.format(scheme))


def include(patterns):
    '''Create filter from inclusion `patterns`.'''
    if not patterns:
        # trivial case: exclude everything
        return lambda x: x[0:0]
    patterns = tuple(map(searcher, patterns))
    # handle general case for inclusion
    return partial(filter, lambda x: any(p(x) for p in patterns))


def exclude(patterns):
    '''Create filter from exclusion `patterns`.'''
    if not patterns:
        # trivial case: include everything
        return lambda x: x
    patterns = tuple(map(searcher, patterns))
    # handle general case for exclusion
    return partial(filterfalse, lambda x: any(p(x) for p in patterns))


def detect(patterns):
    '''Create filter from inclusion `patterns`.'''
    patterns = tuple(map(searcher, patterns))
    return lambda x: any(p(x[0]) for p in patterns)
