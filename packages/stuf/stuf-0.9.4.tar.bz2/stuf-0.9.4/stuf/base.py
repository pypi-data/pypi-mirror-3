# -*- coding: utf-8 -*-
'''stuf base.'''

import sys
from functools import partial
from keyword import iskeyword
from operator import itemgetter
from importlib import import_module
from collections import Sequence, Mapping

getframe = partial(sys._getframe, 1)
identity = lambda x: x
isnone = lambda x, y: x if y is None else y
first = itemgetter(0)
second = itemgetter(1)
maporseq = lambda x: isinstance(x, (Mapping, Sequence))
ismapping = lambda x: isinstance(x, Mapping)
issequence = lambda x: isinstance(x, Sequence)
# illegal characters for Python names
ic = frozenset('()[]{}@,:`=;+*/%&|^><\'"#\\$?!~'.split())


def docit(callable, doc):
    '''Add documentation to a callable.'''
    callable.__doc__ = doc
    return callable


def checkname(name, ic=ic, ik=iskeyword):
    '''Ensures `name` is legal for Python.'''
    # Remove characters that are illegal in a Python name
    name = name.strip().lower().replace('-', '_').replace(
        '.', '_'
    ).replace(' ', '_')
    name = ''.join(i for i in name if i not in ic)
    # add _ if value is Python keyword
    return name + '_' if ik(name) else name


def importer(path, attribute=None, i=import_module, g=getattr):
    '''Import module `path`, optionally with `attribute`.'''
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


def backport(*paths):
    '''Go through import `paths` until one imports or everything fails.'''
    load = None
    for path in paths:
        try:
            load = importer(path)
            break
        except ImportError:
            continue
    if load is None:
        raise ImportError('no path')
    return load
