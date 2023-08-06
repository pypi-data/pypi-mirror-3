# -*- coding: utf-8 -*-
'''knife support'''

from itertools import chain
from pickletools import genops
from functools import update_wrapper
try:
    from cPickle import loads as ld, dumps, HIGHEST_PROTOCOL
except ImportError:
    from pickle import loads as ld, dumps, HIGHEST_PROTOCOL  # @UnusedImport
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # @UnusedImport
from collections import MutableMapping

try:
    from __builtin__ import intern
except ImportError:
    from sys import intern

from stuf.utils import recursive_repr
from stuf.six import items, map as imap, b, function_code
from stuf.six.moves import filterfalse, zip_longest  # @UnresolvedImport @UnusedImport @IgnorePep8
from stuf.six import OrderedDict, items, map as imap, b


def memoize(f, i=intern, z=items, r=repr, uw=update_wrapper):
    f.cache = {}
    if function_code(f).co_argcount == 1:
        def memoize_(arg):
            return f.cache.setdefault(i(r(arg)), f(arg))
    else:
        def memoize_(*args, **kw): #@IgnorePep8
            return f.cache.setdefault(
                i(r(args, z(kw)) if kw else r(args)), f(*args, **kw)
            )
    return uw(f, memoize_)


ichain = chain.from_iterable
loads = memoize(lambda x: ld(x))


@memoize
def optimize(obj, d=dumps, p=HIGHEST_PROTOCOL, s=set, g=genops, b_=b, n=next):
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
        except StopIteration:
            pass
    # Copy the pickle string except for PUTS without a corresponding GET
    def iterthingy(iterthing=iterthing(), this=this, n=n):  # @IgnorePep8
        i = 0
        try:
            while 1:
                arg, start, stop = n(iterthing)
                yield this[i:stop if (arg in gets) else start]
                i = stop
        except StopIteration:
            pass
        yield this[i:]
    return b_('').join(i for i in iterthingy())


def count(iterable, enumerate=enumerate, next=next):
    counter = enumerate(iterable, 1)
    idx = ()
    while 1:
        try:
            idx = next(counter)
        except StopIteration:
            try:
                return next(idx.__iter__())
            except StopIteration:
                return 0


import sys
if not sys.version_info[0] == 2 and sys.version_info[1] < 7:
    from collections import Counter  # @UnresolvedImport
else:
    from heapq import nlargest
    from operator import itemgetter

    class Counter(dict):

        '''dict subclass for counting hashable items'''

        def __init__(self, iterable=None, **kw):
            '''
            If given, count elements from an input iterable. Or, initialize
            count from another mapping of elements to their counts.
            '''
            super(Counter, self).__init__()
            self.update(iterable, **kw)

        def most_common(self, n=None, nl=nlargest, i=items, g=itemgetter):
            '''
            list the n most common elements and their counts from the most
            common to the least

            If n is None, then list all element counts.
            '''
            # Emulate Bag.sortedByCount from Smalltalk
            if n is None:
                return sorted(i(self), key=g(1), reverse=True)
            return nl(n, i(self), key=g(1))

        # Override dict methods where necessary

        def update(self, iterable=None):
            '''like dict.update() but add counts instead of replacing them'''
            if iterable is not None:
                self_get = self.get
                for elem in iterable:
                    self[elem] = self_get(elem, 0) + 1


try:
    from collections import ChainMap  # @UnusedImport
except ImportError:
    # not until Python >= 3.3
    class ChainMap(MutableMapping):

        '''
        ChainMap groups multiple dicts (or other mappings) together to create a
        single, updateable view.

        The underlying mappings are stored in a list.  That list is public and
        can accessed or updated using the *maps* attribute.  There is no other
        state.

        Lookups search the underlying mappings successively until a key is
        found. In contrast, writes, updates, and deletions only operate on the
        first mapping.
        '''

        def __init__(self, *maps):
            '''
            Initialize a ChainMap by setting *maps* to the given mappings.
            If no mappings are provided, a single empty dictionary is used.
            '''
            # always at least one map
            self.maps = list(maps) or [OrderedDict()]

        def __missing__(self, key):
            raise KeyError(key)

        def __getitem__(self, key):
            for mapping in self.maps:
                try:
                    # can't use 'key in mapping' with defaultdict
                    return mapping[key]
                except KeyError:
                    pass
            # support subclasses that define __missing__
            return self.__missing__(key)

        def get(self, key, default=None):
            return self[key] if key in self else default

        def __len__(self):
            # reuses stored hash values if possible
            return len(set().union(*self.maps))

        def __iter__(self, set=set):
            return set().union(*self.maps).__iter__()

        def __contains__(self, key, any=any):
            return any(key in m for m in self.maps)

        def __bool__(self, any=any):
            return any(self.maps)

        @recursive_repr
        def __repr__(self):
            return '{0.__class__.__name__}({1})'.format(
                self, ', '.join(imap(repr, self.maps))
            )

        @classmethod
        def fromkeys(cls, iterable, *args):
            '''
            Create a ChainMap with a single dict created from the iterable.
            '''
            return cls(dict.fromkeys(iterable, *args))

        def copy(self):
            '''
            New ChainMap or subclass with a new copy of maps[0] and refs to
            maps[1:]
            '''
            return self.__class__(self.maps[0].copy(), *self.maps[1:])

        __copy__ = copy

        def new_child(self):
            '''New ChainMap with a new dict followed by all previous maps.'''
            # like Django's Context.push()
            return self.__class__({}, *self.maps)

        @property
        def parents(self):
            '''New ChainMap from maps[1:].'''
            # like Django's Context.pop()
            return self.__class__(*self.maps[1:])

        def __setitem__(self, key, value):
            self.maps[0][key] = value

        def __delitem__(self, key):
            try:
                del self.maps[0][key]
            except KeyError:
                raise KeyError(
                    'Key not found in the first mapping: {!r}'.format(key)
                )

        def popitem(self):
            '''
            Remove and return an item pair from maps[0]. Raise KeyError is
            maps[0] is empty.
            '''
            try:
                return self.maps[0].popitem()
            except KeyError:
                raise KeyError('No keys found in the first mapping.')

        def pop(self, key, *args):
            '''
            Remove *key* from maps[0] and return its value. Raise KeyError if
            *key* not in maps[0].
            '''
            try:
                return self.maps[0].pop(key, *args)
            except KeyError:
                raise KeyError(
                    'Key not found in the first mapping: {!r}'.format(key)
                )

        def clear(self):
            '''Clear maps[0], leaving maps[1:] intact.'''
            self.maps[0].clear()
