# -*- coding: utf-8 -*-
'''stuf search.'''

from os import sep
from functools import partial
from keyword import iskeyword

from stuf.utils import lru
from parse import compile as pcompile
from stuf.six.moves import filterfalse  # @UnresolvedImport
from stuf.six import isstring, filter, map, first, rcompile, rescape, rsub

regex = lambda expr, flag: rcompile(expr, flag).search
parse = lambda expr, flag: pcompile(expr)._search_re.search
glob = lambda expr, flag: rcompile(globpattern(expr), flag).search
SEARCH = dict(parse=parse, glob=glob, regex=regex)
# Illegal characters for Python names
ic = frozenset('()[]{}@,:`=;+*/%&|^><\'"#\\$?!~'.split())


def checkname(name, ic=ic, ik=iskeyword):
    '''Ensures `name` is legal Python name.'''
    # Remove characters that are illegal in a Python name
    name = name.strip().lower().replace('-', '_').replace(
        '.', '_'
    ).replace(' ', '_')
    name = ''.join(i for i in name if i not in ic)
    # Add _ if value is a Python keyword
    return name + '_' if ik(name) else name


def detect(patterns):
    '''Create filter from inclusion `patterns`.'''
    patterns = tuple(map(searcher, patterns))
    return lambda x: any(p(first(x)) for p in patterns)


def exclude(patterns):
    '''Create filter from exclusion `patterns`.'''
    if not patterns:
        # trivial case: include everything
        return lambda x: x
    patterns = tuple(map(searcher, patterns))
    # handle general case for exclusion
    return partial(filterfalse, lambda x: any(p(x) for p in patterns))


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


def include(patterns):
    '''Create filter from inclusion `patterns`.'''
    if not patterns:
        # trivial case: exclude everything
        return lambda x: x[0:0]
    patterns = tuple(map(searcher, patterns))
    # handle general case for inclusion
    return partial(filter, lambda x: any(p(x) for p in patterns))


@lru()
def searcher(expr, flag=32):
    '''Build search function from `expr`.'''
    try:
        scheme, expr = expr.split(':', 1) if isstring(expr) else expr
        return SEARCH[scheme](expr, flag)
    except KeyError:
        raise TypeError('"{0}" is not a valid search scheme'.format(scheme))
