# -*- coding: utf-8 -*-
'''
Support for wildcard pattern matching in object inspection.

Authors
-------
- Jorgen Stenarson <jorgen.stenarson@bostream.nu>
- Thomas Kluyver
'''

import re
import types


def get_class_members(cls):
    ret = dir(cls)
    if hasattr(cls, '__bases__'):
        try:
            bases = cls.__bases__
        except AttributeError:
            # `obj` lied to hasattr (e.g. Pyro), ignore
            pass
        else:
            for base in bases:
                ret.extend(get_class_members(base))
    return ret


def dir2(obj):
    '''
    dir2(obj) -> list of strings

    Extended version of the Python builtin dir(), which does a few extra
    checks, and supports common objects with unusual internals that confuse
    dir(), such as Traits and PyCrust.

    This version is guaranteed to return only a list of true strings, whereas
    dir() returns anything that objects inject into themselves, even if they
    are later not really valid for attribute access (many extension libraries
    have such bugs).
    '''
    # Start building the attribute list via dir(), and then complete it
    # with a few extra special-purpose calls.
    words = dir(obj)
    if hasattr(obj, '__class__'):
        words.append('__class__')
        words.extend(get_class_members(obj.__class__))
    #if '__base__' in words: 1/0
    # Some libraries (such as traits) may introduce duplicates, we want to
    # track and clean this up if it happens
    may_have_dupes = False
    # this is the 'dir' function for objects with Enthought's traits
    if hasattr(obj, 'trait_names'):
        try:
            words.extend(obj.trait_names())
            may_have_dupes = True
        except TypeError:
            # This will happen if `obj` is a class and not an instance.
            pass
        except AttributeError:
            # `obj` lied to hasatter (e.g. Pyro), ignore
            pass
    # Support for PyCrust-style _getAttributeNames magic method.
    if hasattr(obj, '_getAttributeNames'):
        try:
            words.extend(obj._getAttributeNames())
            may_have_dupes = True
        except TypeError:
            # `obj` is a class and not an instance.  Ignore
            # this error.
            pass
        except AttributeError:
            # `obj` lied to hasatter (e.g. Pyro), ignore
            pass
    if may_have_dupes:
        # eliminate possible duplicates, as some traits may also
        # appear as normal attributes in the dir() call.
        words = list(set(words))
        words.sort()
    # filter out non-string attributes which may be stuffed by dir() calls
    # and poor coding in third-party modules
    return [w for w in words if isinstance(w, basestring)]


def create_typestr2type_dicts(dont_include_in_type2typestr=['lambda']):
    '''Return dictionaries mapping lower case typename (e.g. 'tuple') to type
    objects from the types package, and vice versa.'''
    typenamelist = [tname for tname in dir(types) if tname.endswith('Type')]
    typestr2type, type2typestr = {}, {}
    for tname in typenamelist:
        name = tname[:-4].lower()          # Cut 'Type' off the end of the name
        obj = getattr(types, tname)
        typestr2type[name] = obj
        if name not in dont_include_in_type2typestr:
            type2typestr[obj] = name
    return typestr2type, type2typestr

typestr2type, type2typestr = create_typestr2type_dicts()


def is_type(obj, typestr_or_type):
    '''
    is_type(obj, typestr_or_type) verifies if obj is of a certain type. It
    can take strings or actual python types for the second argument, i.e.
    'tuple'<->TupleType. 'all' matches all types.

    TODO: Should be extended for choosing more than one type.
    '''
    if typestr_or_type == 'all':
        return True
    if type(typestr_or_type) == types.TypeType:
        test_type = typestr_or_type
    else:
        test_type = typestr2type.get(typestr_or_type, False)
    if test_type:
        return isinstance(obj, test_type)
    return False


def show_hidden(str, show_all=False):
    '''Return true for strings starting with single _ if show_all is true.'''
    return show_all or str.startswith('__') or not str.startswith('_')


def dict_dir(obj):
    '''
    Produce a dictionary of an object's attributes. Builds on dir2 by
    checking that a getattr() call actually succeeds.
    '''
    ns = {}
    for key in dir2(obj):
        # This seemingly unnecessary try/except is actually needed
        # because there is code out there with metaclasses that
        # create 'write only' attributes, where a getattr() call
        # will fail even if the attribute appears listed in the
        # object's dictionary.  Properties can actually do the same
        # thing.  In particular, Traits use this pattern
        try:
            ns[key] = getattr(obj, key)
        except AttributeError:
            pass
    return ns


def filter_ns(ns, name_pattern='*', type_pattern='all', ignore_case=True,
            show_all=True):
    '''Filter a namespace dictionary by name pattern and item type.'''
    pattern = name_pattern.replace('*', '.*').replace('?', '.')
    if ignore_case:
        reg = re.compile(pattern + '$', re.I)
    else:
        reg = re.compile(pattern + '$')
    # Check each one matches regex; shouldn't be hidden; of correct type.
    return dict((key, obj) for key, obj in ns.iteritems() if all([
        reg.match(key),
        show_hidden(key, show_all),
        is_type(obj, type_pattern)])
    )


def list_namespace(
    namespace, type_pattern, filter, ignore_case=False, show_all=False
):
    '''
    Return dictionary of all objects in a namespace dictionary that match
    type_pattern and filter.'''
    pattern_list = filter.split('.')
    if len(pattern_list) == 1:
        return filter_ns(
            namespace,
            name_pattern=pattern_list[0],
            type_pattern=type_pattern,
            ignore_case=ignore_case,
            show_all=show_all,
        )
    else:
        # This is where we can change if all objects should be searched or
        # only modules. Just change the type_pattern to module to search only
        # modules
        filtered = filter_ns(
            namespace,
            name_pattern=pattern_list[0],
            type_pattern='all',
            ignore_case=ignore_case,
            show_all=show_all,
        )
        results = {}
        for name, obj in filtered.iteritems():
            ns = list_namespace(
                dict_dir(obj),
                type_pattern,
                '.'.join(pattern_list[1:]
            ),
            ignore_case=ignore_case, show_all=show_all)
            for inner_name, inner_obj in ns.iteritems():
                results['%s.%s' % (name, inner_name)] = inner_obj
        return results
