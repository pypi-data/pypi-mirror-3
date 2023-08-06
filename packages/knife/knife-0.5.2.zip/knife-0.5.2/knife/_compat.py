# -*- coding: utf-8 -*-
'''knife support'''

from itertools import chain
from pickletools import genops
from functools import update_wrapper
try:
    import cPickle as pickle
except ImportError:
    import pickle  # @UnusedImport
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # @UnusedImport
from collections import MutableMapping, deque

try:
    from __builtin__ import intern
except ImportError:
    from sys import intern

from stuf.six import items, map as imap, b
from stuf.utils import OrderedDict, recursive_repr
from stuf.six.moves import filterfalse, zip_longest  # @UnresolvedImport @UnusedImport @IgnorePep8


def memoize(f, i=intern, z=items, r=repr, uw=update_wrapper):
    f.cache = {}
    def memoize_(*args, **kw): #@IgnorePep8
        return f.cache.setdefault(
            i(r(args, z(kw)) if kw else r(args)), f(*args, **kw)
        )
    return uw(f, memoize_)


ichain = chain.from_iterable
ifilterfalse = filterfalse
dumps = pickle.dumps
protocol = pickle.HIGHEST_PROTOCOL
loads = memoize(lambda x: pickle.loads(x))


@memoize
def optimize(obj, d=dumps, p=protocol, s=set, q=deque, g=genops):
    '''
    Optimize a pickle string by removing unused PUT opcodes.

    Raymond Hettinger Python cookbook recipe # 545418
    '''
    # set of args used by a GET opcode
    this = d(obj, p)
    gets = s()
    gadd = gets.add
    # (arg, startpos, stoppos) for the PUT opcodes
    puts = q()
    pappend = puts.append
    # set to pos if previous opcode was a PUT
    prevpos, prevarg = None, None
    for opcode, arg, pos in genops(this):
        if prevpos is not None:
            pappend((prevarg, prevpos, pos))
            prevpos = None
        if 'PUT' in opcode.name:
            prevarg, prevpos = arg, pos
        elif 'GET' in opcode.name:
            gadd(arg)
    # Copy the pickle string except for PUTS without a corresponding GET
    s = q()
    sappend = s.append
    i = 0
    for arg, start, stop in puts:
        sappend(this[i:stop if (arg in gets) else start])
        i = stop
    sappend(this[i:])
    return b('').join(s)


def count(iterable, enumerate=enumerate, next=next, iter=iter):
    counter = enumerate(iterable, 1)
    idx = ()
    while 1:
        try:
            idx = next(counter)
        except StopIteration:
            return next(iter(idx), 0)


import sys
if not sys.version_info[0] == 2 and sys.version_info[1] < 7:
    from collections import Counter  # @UnresolvedImport
else:
    import heapq
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

        def most_common(self, n=None):
            '''
            list the n most common elements and their counts from the most
            common to the least

            If n is None, then list all element counts.
            '''
            # Emulate Bag.sortedByCount from Smalltalk
            if n is None:
                return sorted(items(self), key=itemgetter(1), reverse=True)
            return heapq.nlargest(n, self.iteritems(), key=itemgetter(1))

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

        def __iter__(self, set=set, iter=iter):
            return iter(set().union(*self.maps))

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
