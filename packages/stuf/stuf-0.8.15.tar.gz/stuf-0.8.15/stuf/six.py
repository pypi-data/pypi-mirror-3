# -*- coding: utf-8 -*-
# pylint: disable-msg=f0401,w0613,w0631,w0622,w0122
'''utilities for writing code that runs on Python 2 and 3'''

import sys
import types
import operator
try:
    from future_builtins import filter, map, zip
except ImportError:
    from builtins import filter, map, zip  # @UnusedImport
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # @UnusedImport
try:
    from collections import OrderedDict
except  ImportError:
    from ordereddict import OrderedDict  # @UnusedImport
try:
    from thread import get_ident
except ImportError:
    try:
        from dummy_thread import get_ident
    except ImportError:
        from _thread import get_ident  # @UnusedImport

__author__ = 'Benjamin Peterson <benjamin@python.org>'
__version__ = '1.1.0'

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3
if PY3:
    strings = str,
    integers = int,
    classes = type,
    native = texts = str
    binaries = bytes
    MAXSIZE = sys.maxsize
else:
    strings = basestring,
    integers = (int, long)
    classes = (type, types.ClassType)
    texts = unicode
    native = binaries = str

    # It's possible to have sizeof(long) != sizeof(Py_ssize_t).
    class X(object):
        def __len__(self):
            return 1 << 31
    try:
        len(X())
    except OverflowError:
        # 32-bit
        MAXSIZE = int((1 << 31) - 1)
    else:
        # 64-bit
        MAXSIZE = int((1 << 63) - 1)
    del X


def _add_doc(func, doc):
    '''add documentation to a function.'''
    func.__doc__ = doc


def _import_module(name):
    '''import module, returning the module after the last dot.'''
    __import__(name)
    return sys.modules[name]


class _LazyDescr(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, tp):
        result = self._resolve()
        setattr(obj, self.name, result)
        # This is a bit ugly, but it avoids running this again.
        delattr(tp, self.name)
        return result


class MovedModule(_LazyDescr):

    def __init__(self, name, old, new=None):
        super(MovedModule, self).__init__(name)
        if PY3:
            if new is None:
                new = name
            self.mod = new
        else:
            self.mod = old

    def _resolve(self):
        return _import_module(self.mod)


class MovedAttribute(_LazyDescr):

    def __init__(self, name, old_mod, new_mod, old_attr=None, new_attr=None):
        super(MovedAttribute, self).__init__(name)
        if PY3:
            if new_mod is None:
                new_mod = name
            self.mod = new_mod
            if new_attr is None:
                if old_attr is None:
                    new_attr = name
                else:
                    new_attr = old_attr
            self.attr = new_attr
        else:
            self.mod = old_mod
            if old_attr is None:
                old_attr = name
            self.attr = old_attr

    def _resolve(self):
        module = _import_module(self.mod)
        return getattr(module, self.attr)


class _MovedItems(types.ModuleType):

    '''lazy loading of moved objects'''


_moved_attributes = [
    MovedAttribute(
        'GeneratorContextManager',
        'contextlib',
        'contextlib',
        'GeneratorContextManager',
        '_GeneratorContextManager',
    ),
    MovedAttribute(
        'filterfalse', 'itertools', 'itertools', 'ifilterfalse', 'filterfalse',
    ),
    MovedAttribute(
        'zip_longest', 'itertools', 'itertools', 'izip_longest', 'zip_longest',
    ),
    MovedAttribute('cStringIO', 'cStringIO', 'io', 'StringIO'),
    MovedAttribute('reload_module', '__builtin__', 'imp', 'reload'),
    MovedAttribute('reduce', '__builtin__', 'functools'),
    MovedAttribute('StringIO', 'StringIO', 'io'),
    MovedAttribute('xrange', '__builtin__', 'builtins', 'xrange', 'range'),
    MovedAttribute('parsedate_tz', 'rfc822', 'email.utils', 'parsedate_tz'),
    MovedAttribute('formatdate', 'rfc822', 'email.utils', 'formatdate'),
    MovedAttribute('parse_qs', 'cgi', 'urllib.parse', 'parse_qs'),
    MovedAttribute('urlencode', 'urllib', 'urllib.parse', 'urlencode'),
    MovedModule('builtins', '__builtin__'),
    MovedModule('configparser', 'ConfigParser'),
    MovedModule('copyreg', 'copy_reg'),
    MovedModule('http_cookiejar', 'cookielib', 'http.cookiejar'),
    MovedModule('http_cookies', 'Cookie', 'http.cookies'),
    MovedModule('html_entities', 'htmlentitydefs', 'html.entities'),
    MovedModule('html_parser', 'HTMLParser', 'html.parser'),
    MovedModule('http_client', 'httplib', 'http.client'),
    MovedModule('BaseHTTPServer', 'BaseHTTPServer', 'http.server'),
    MovedModule('CGIHTTPServer', 'CGIHTTPServer', 'http.server'),
    MovedModule('SimpleHTTPServer', 'SimpleHTTPServer', 'http.server'),
    MovedModule('pickle', 'cPickle', 'pickle'),
    MovedModule('queue', 'Queue'),
    MovedModule('reprlib', 'repr'),
    MovedModule('socketserver', 'SocketServer'),
    MovedModule('urllib_robotparser', 'robotparser', 'urllib.robotparser'),
    MovedModule('winreg', '_winreg'),
    MovedModule('xmlrpc', 'xmlrpclib', 'xmlrpc.client'),
]
for attr in _moved_attributes:
    setattr(_MovedItems, attr.name, attr)
del attr

moves = sys.modules['stuf.six.moves'] = _MovedItems('moves')


def add_move(move):
    '''Add an item to six.moves.'''
    setattr(_MovedItems, move.name, move)


def remove_move(name):
    '''Remove item from six.moves.'''
    try:
        delattr(_MovedItems, name)
    except AttributeError:
        try:
            del moves.__dict__[name]
        except KeyError:
            raise AttributeError('no such move, %r' % (name,))

if PY3:
    _meth_func = '__func__'
    _meth_self = '__self__'
    _func_code = '__code__'
    _func_defaults = '__defaults__'

    _iterkeys = 'keys'
    _itervalues = 'values'
    _iteritems = 'items'
else:
    _meth_func = 'im_func'
    _meth_self = 'im_self'
    _func_code = 'func_code'
    _func_defaults = 'func_defaults'

    _iterkeys = 'keys'
    _itervalues = 'values'
    _iteritems = 'items'

try:
    advance_iterator = next
except NameError:
    def advance_iterator(it):
        return it.next()
next = advance_iterator

if PY3:
    def get_unbound_function(unbound):
        return unbound

    Iterator = object

    def callable(obj):
        return any('__call__' in klass.__dict__ for klass in type(obj).__mro__)
else:
    def get_unbound_function(unbound):
        return unbound.im_func

    class Iterator(object):
        def next(self):
            return type(self).__next__(self)

    callable = callable

_add_doc(
    get_unbound_function, 'Get the function out of a possibly unbound function'
)

method_function = operator.attrgetter(_meth_func)
method_self = operator.attrgetter(_meth_self)
function_code = operator.attrgetter(_func_code)
function_defaults = operator.attrgetter(_func_defaults)


def keys(d):
    '''Return an iterator over the keys of a dictionary.'''
    return getattr(d, _iterkeys)()


def values(d):
    '''Return an iterator over the values of a dictionary.'''
    return getattr(d, _itervalues)()


def items(d):
    '''Return an iterator over the (key, value) pairs of a dictionary.'''
    return getattr(d, _iteritems)()


if PY3:
    def b(s):
        return s.encode('latin-1')

    def u(s):
        return s
    if sys.version_info[1] <= 1:
        def int2byte(i):
            return bytes((i,))
    else:
        # This is about 2x faster than the implementation above on 3.2+
        int2byte = operator.methodcaller('to_bytes', 1, 'big')
    import io
    StringIO = io.StringIO
    BytesIO = io.BytesIO
else:
    def b(s):
        return s

    def u(s):
        return unicode(s, 'unicode_escape')
    int2byte = chr
    import StringIO
    StringIO = BytesIO = StringIO.StringIO
_add_doc(b, '''Byte literal''')
_add_doc(u, '''Text literal''')

if PY3:
    import builtins  # @UnresolvedImport
    exec_ = getattr(builtins, 'exec')

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
    printf = getattr(builtins, 'print')
    del builtins
else:
    def exec_(code, globs=None, locs=None):
        '''Execute code in a namespace.'''
        if globs is None:
            frame = sys._getframe(1)
            globs = frame.f_globals
            if locs is None:
                locs = frame.f_locals
            del frame
        elif locs is None:
            locs = globs
        exec('''exec code in globs, locs''')

    exec_('''def reraise(tp, value, tb=None):
    raise tp, value, tb
''')

    def printf(*args, **kw):
        '''The new-style print function.'''
        fp = kw.pop('file', sys.stdout)
        if fp is None:
            return

        def write(data):
            if not isinstance(data, basestring):
                data = str(data)
            fp.write(data)
        want_unicode = False
        sep = kw.pop('sep', None)
        if sep is not None:
            if isinstance(sep, unicode):
                want_unicode = True
            elif not isinstance(sep, str):
                raise TypeError('sep must be None or a string')
        end = kw.pop('end', None)
        if end is not None:
            if isinstance(end, unicode):
                want_unicode = True
            elif not isinstance(end, str):
                raise TypeError('end must be None or a string')
        if kw:
            raise TypeError('invalid keyword arguments to print()')
        if not want_unicode:
            for arg in args:
                if isinstance(arg, unicode):
                    want_unicode = True
                    break
        if want_unicode:
            newline = unicode('\n')
            space = unicode(' ')
        else:
            newline = '\n'
            space = ' '
        if sep is None:
            sep = space
        if end is None:
            end = newline
        for i, arg in enumerate(args):
            if i:
                write(sep)
            write(arg)
        write(end)

_add_doc(reraise, '''Reraise an exception.''')


def with_metaclass(meta, base=object):
    '''Create a base class with a metaclass.'''
    return meta('NewBase', (base,), {})


class port(object):

    '''python 2/3 helper'''

    # is python 3?
    PY3 = PY3
    # types
    BINARY = binaries
    CLASS = classes
    INTEGER = integers
    MAXSIZE = MAXSIZE
    STRING = strings
    UNICODE = texts
    # classes
    BytesIO = BytesIO
    StringIO = StringIO
    # character data
    b = staticmethod(b)
    int2byte = staticmethod(int2byte)
    u = staticmethod(u)
    # dictionary
    items = staticmethod(items)
    keys = staticmethod(keys)
    values = staticmethod(values)
    # iterables
    iterator = staticmethod(advance_iterator)
    # classes
    metaclass = staticmethod(with_metaclass)
    # methods
    code = staticmethod(function_code)
    defaults = staticmethod(function_defaults)
    method_function = staticmethod(method_function)
    method_self = staticmethod(method_self)
    unbound = staticmethod(get_unbound_function)
    # exception
    reraise = staticmethod(reraise)

    @classmethod
    def isbinary(cls, value):
        '''is binary?'''
        return isinstance(value, cls.BINARY)

    @classmethod
    def isclass(cls, value):
        '''is class?'''
        return isinstance(value, cls.CLASS)

    @classmethod
    def iscall(cls, value):
        '''is callable?'''
        return callable(value)

    @classmethod
    def isgtemax(cls, value):
        '''greater than max size?'''
        return value > cls.MAXSIZE

    @classmethod
    def isinteger(cls, value):
        '''is integer?'''
        return isinstance(value, cls.INTEGER)

    @classmethod
    def isltemax(cls, value):
        '''less than max size?'''
        return value < cls.MAXSIZE

    @classmethod
    def isstring(cls, value):
        '''is string'''
        return isinstance(value, cls.STRING)

    @classmethod
    def isunicode(cls, value):
        '''is text?'''
        return isinstance(value, cls.UNICODE)

    @staticmethod
    def printf(*args, **kw):
        '''print output'''
        return printf(*args, **kw)

isbinary = port.isbinary
isstring = port.isstring
isunicode = port.isunicode


def tounicode(thing, encoding='utf-8', errors='strict'):
    return (
        thing.decode(encoding, errors) if isbinary(thing) else
        texts(texts(thing).encode(encoding, errors), encoding, errors)
    )


def tobytes(thing, encoding='utf-8', errors='strict'):
    return (
        texts(thing).encode(encoding, errors) if not isbinary(thing) else thing
    )
