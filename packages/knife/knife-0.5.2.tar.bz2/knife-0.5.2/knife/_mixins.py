# -*- coding: utf-8 -*-
'''specific knife mixins'''

from math import fsum
from copy import deepcopy
from threading import local
from inspect import isclass, getmro
from functools import reduce, partial
from random import shuffle, randrange
from collections import deque, namedtuple
from operator import methodcaller, itemgetter, attrgetter, truediv
from itertools import (
    groupby, islice, tee, starmap, repeat, combinations, permutations, chain)

from stuf.six import (
    strings, items, values, keys, filter, map)
from stuf.utils import OrderedDict, selfname, deferiter, deferfunc

from knife._compat import (
    Counter, ChainMap, ichain, ifilterfalse, zip_longest, count, memoize)

Count = namedtuple('Count', 'least most overall')
MinMax = namedtuple('MinMax', 'min max')
TrueFalse = namedtuple('TrueFalse', 'true false')
GroupBy = namedtuple('Group', 'keys groups')
slice = lambda x, y: next(islice(x, y, None))


class _CmpMixin(local):

    '''comparing mixin'''

    @staticmethod
    @memoize
    def _all(truth, all_=all, imap_=map):
        # invoke worker on each item to yield truth
        return lambda x: all_(imap_(truth, x))

    @staticmethod
    @memoize
    def _any(truth, any_=any, imap_=map):
        # invoke worker on each item to yield truth
        return lambda x: any_(imap_(truth, x))

    @staticmethod
    @memoize
    def _difference(symmetric, reduce_=reduce, set_=set, partial_=partial):
        if symmetric:
            test = lambda x, y: set_(x).symmetric_difference(y)
        else:
            test = lambda x, y: set_(x).difference(y)
        return partial_(reduce_, test)

    @staticmethod
    def _intersection(iterable, set_=set, reduce_=reduce):
        return reduce_(lambda x, y: set_(x).intersection(y), iterable)

    @staticmethod
    def _union(iterable, set_=set, reduce_=reduce):
        return reduce_(lambda x, y: set_(x).union(y), iterable)

    @staticmethod
    @memoize
    def _unique(key, set_=set):
        def unique(iterable):
            seen = set_()
            seenadd, key_ = seen.add, key
            for element in iterable:
                k = key_(element)
                if k not in seen:
                    seenadd(k)
                    yield element
        return unique


class _MathMixin(local):

    '''number mixin'''

    @staticmethod
    def _average(iterable, s=sum, t=truediv, n=count, e=tee):
        i1, i2 = e(iterable)
        yield t(s(i1, 0.0), n(i2))

    @staticmethod
    def _count(iterable, counter_=Counter, count_=Count):
        count = counter_(iterable)
        commonality = count.most_common()
        yield count_(
            # least common
            commonality[:-2:-1][0][0],
            # most common (mode)
            count.most_common(1)[0][0],
            # overall commonality
            commonality,
        )

    @staticmethod
    @memoize
    def _max(key, imax_=max):
        def imax(iterable):
            yield imax_(iterable, key=key)
        return imax

    @staticmethod
    def _median(iterable, s=sorted, d=truediv, int=int, count=count):
        i1, i2 = tee(s(iterable))
        e = d(count(i1) - 1, 2)
        p = int(e)
        if e % 2 == 0:
            yield slice(i2, p)
        else:
            i3, i4 = tee(i2)
            yield truediv(slice(i3, p) + slice(i4, p + 1), 2)

    @staticmethod
    def _minmax(iterable, imin=min, imax=max, tee_=tee, minmax_=MinMax):
        i1, i2 = tee_(iterable)
        yield minmax_(imin(i1), imax(i2))

    @staticmethod
    def _range(iterable, d=deque, sorted_=sorted):
        i1, i2 = tee(sorted_(iterable))
        yield d(i1, maxlen=1).pop() - next(i2)

    @staticmethod
    @memoize
    def _min(key, imin_=min):
        def imin(iterable):
            yield imin_(iterable, key=key)
        return imin

    @staticmethod
    @memoize
    def _sum(start, floats, isum_=sum, fsum_=fsum):
        summer_ = fsum_ if floats else lambda x: isum_(x, start)
        def isum(iterable): #@IgnorePep8
            yield summer_(iterable)
        return isum


class _OrderMixin(local):

    '''order mixin'''

    @staticmethod
    @memoize
    def _group(key, group_=groupby, sorted_=sorted, G=GroupBy, tuple_=tuple):
        def grouper(iterable):
            for k, g in group_(sorted_(iterable, key=key), key):
                yield G(k, tuple_(g))
        return grouper

    @staticmethod
    def _reverse(iterable, reversed_=reversed, tuple_=tuple):
        for thing in reversed_(tuple_(iterable)):
            yield thing

    @staticmethod
    def _shuffle(iterable, list_=list, shuffle_=shuffle):
        iterable = list_(iterable)
        shuffle_(iterable)
        yield iterable

    @staticmethod
    @memoize
    def _sort(key, sorted_=sorted):
        def isort(iterable):
            yield sorted_(iterable, key=key)
        return isort


class _RepeatMixin(local):

    '''repetition mixin'''

    @staticmethod
    def _combinations(n, combinations_=combinations):
        return lambda x: combinations_(x, n)

    @staticmethod
    def _copy(iterable, deepcopy_=deepcopy, imap_=map):
        return imap_(deepcopy_, iterable)

    @staticmethod
    def _permutations(n, permutations_=permutations):
        return lambda x: permutations_(x, n)

    @staticmethod
    @memoize
    def _repeat(n, use, call, r=repeat, t=tuple, s=starmap):
        if use:
            return lambda x: s(call, r(t(x), n))
        return lambda x: r(t(x), n)


class _MapMixin(local):

    '''mapping mixin'''

    @staticmethod
    @memoize
    def _argmap(call, curr, arg, starmap_=starmap, partial_=partial):
        if curr:
            def argmap(*args):
                return call(*(args + arg))
        else:
            argmap = call
        return partial_(starmap_, argmap)

    @staticmethod
    @memoize
    def _invoke(name, args, mc_=methodcaller, imap_=map, partial_=partial):
        caller = mc_(name, *args[0], **args[1])
        def invoke(thing): #@IgnorePep8
            read = caller(thing)
            return thing if read is None else read
        return partial_(imap_, invoke)

    @staticmethod
    @memoize
    def _kwargmap(call, curr, arg, kw, starmap_=starmap, partial_=partial):
        if curr:
            def kwargmap(*params):
                args, kwargs = params
                kwargs.update(kw)
                return call(*(args + arg), **kwargs)
        else:
            kwargmap = lambda x, y: call(*x, **y)
        return partial_(starmap_, kwargmap)

    @staticmethod
    @memoize
    def _map(call, imap_=map, partial_=partial):
        return partial_(imap_, call)

    @staticmethod
    @memoize
    def _mapping(call, key, value, k=keys, i=items, v=values, c=ichain, m=map):
        if key:
            return lambda x: m(call, c(m(k, x)))
        elif value:
            return lambda x: m(call, c(m(v, x)))
        return lambda x: starmap(call, c(m(i, x)))


class _FilterMixin(local):

    '''filtering mixin'''

    @staticmethod
    @memoize
    def _attributes(names, _attrgetter=attrgetter):
        attrfind = _attrgetter(*names)
        def attrs(iterable, get=attrfind): #@IgnorePep8
            AttrErr_ = AttributeError
            for thing in iterable:
                try:
                    yield get(thing)
                except AttrErr_:
                    pass
        return attrs

    @staticmethod
    @memoize
    def _duality(true, f=filter, ff=ifilterfalse, u=tuple, t=tee, b=TrueFalse):
        def duality(iterable): #@IgnorePep8
            truth_, false_ = t(iterable)
            yield b(u(f(true, truth_)), u(ff(true, false_)))
        return duality

    @staticmethod
    @memoize
    def _filter(true, false, f_=filter, ff_=ifilterfalse, partial_=partial):
        return partial_(ff_, true) if false else partial_(f_, true)

    @staticmethod
    @memoize
    def _items(key, itemgetter_=itemgetter):
        itemfind = itemgetter_(*key)
        def itemz(iterable, get=itemfind): #@IgnorePep8
            IndexErr_, KeyErr_, TypeErr_ = IndexError, KeyError, TypeError
            for thing in iterable:
                try:
                    yield get(thing)
                except (IndexErr_, KeyErr_, TypeErr_):
                    pass
        return itemz

    @staticmethod
    @memoize
    def _traverse(test, invert, odict_=OrderedDict, chain_=chain, vars_=vars):
        ifilter = ifilterfalse if invert else filter
        def members(iterable, beenthere=None): #@IgnorePep8
            isclass_ = isclass
            getattr_ = getattr
            o_ = odict_
            members_ = members
            ifilter_ = ifilter
            varz_ = vars_
            if beenthere is None:
                beenthere = set()
            test_ = test
            mro = getmro(iterable)
            names = dir(iterable)
            adder_ = beenthere.add
            for name in names:
                # yes, it's really supposed to be a tuple
                for base in chain_([iterable], mro):
                    var = varz_(base)
                    if name in var:
                        obj = var[name]
                        break
                else:
                    obj = getattr_(iterable, name)
                if obj in beenthere:
                    continue
                else:
                    adder_(obj)
                if isclass_(obj):
                    yield name, o_((k, v) for k, v in ifilter_(
                        test_, members_(obj, beenthere),
                    ))
                else:
                    yield name, obj
        def traverse(iterable): #@IgnorePep8
            isinstance_ = isinstance
            selfname_ = selfname
            members_ = members
            o_ = odict_
            cm_ = ChainMap
            ifilter_ = ifilter
            test_ = test
            for iterator in iterable:
                chaining = cm_()
                chaining['classname'] = selfname_(iterator)
                cappend = chaining.maps.append
                for k, v in ifilter_(test_, members_(iterator)):
                    if isinstance_(v, o_):
                        v['classname'] = k
                        cappend(v)
                    else:
                        chaining[k] = v
                yield chaining
        return traverse


class _ReduceMixin(local):

    '''reduce mixin'''

    @classmethod
    def _flatten(cls, iterable, strings_=strings, isinstance_=isinstance):
        smash_ = cls._flatten
        for item in iterable:
            try:
                # don't recur over strings
                if isinstance_(item, strings_):
                    yield item
                else:
                    # do recur over other things
                    for j in smash_(item):
                        yield j
            except TypeError:
                # does not recur
                yield item

    @staticmethod
    def _merge(iterable, ichain_=ichain):
        return ichain_(iterable)

    @staticmethod
    @memoize
    def _reduce(call, initial, reverse, reduce_=reduce):
        if reverse:
            if initial is None:
                return lambda i: reduce_(lambda x, y: call(y, x), i)
            return lambda i: reduce_(lambda x, y: call(y, x), i, initial)
        if initial is None:
            return lambda x: reduce_(call, x)
        return lambda x: reduce_(call, x, initial)

    @staticmethod
    def _zip(iterable, zip_=zip_longest):
        return zip_(*iterable)


class _SliceMixin(local):

    '''slicing mixin'''

    @staticmethod
    @memoize
    def _at(n, default, islice_=islice, next_=next):
        return lambda x: next_(islice_(x, n, None), default)

    @staticmethod
    @memoize
    def _choice(t=tee, n=next, s=islice, rr=randrange, c=count):
        def choice(iterable):
            i1, i2 = t(iterable)
            yield n(s(i1, rr(0, c(i2)), None))
        return choice

    @staticmethod
    @memoize
    def _dice(n, fill, zip_longest_=zip_longest, iter_=iter):
        return lambda x: zip_longest_(fillvalue=fill, *[iter_(x)] * n)

    @staticmethod
    @memoize
    def _first(n=0, islice_=islice, next_=deferiter):
        return lambda x: islice_(x, n) if n else next_(x)

    @staticmethod
    def _initial(iterable, islice_=islice, tee_=tee, count_=count):
        i1, i2 = tee_(iterable)
        return islice_(i1, count_(i2) - 1)

    @staticmethod
    @memoize
    def _last(n, s=islice, d=deque, t=tee, f=deferfunc, c=count):
        if n:
            def last(iterable):
                i1, i2 = t(iterable)
                return s(i1, c(i2) - n, None)
            return last
        return lambda x: f(d(x, maxlen=1).pop)

    @staticmethod
    def _rest(iterable, islice_=islice):
        return islice_(iterable, 1, None)

    @staticmethod
    @memoize
    def _sample(n, t=tee, s=slice, rr=randrange, m=map, c=count):
        def sample(iterable):
            i1, i2 = t(iterable)
            length = c(i1)
            return m(lambda x: s(x, rr(0, length)), t(i2, n))
        return sample

    @staticmethod
    def _slice(start, stop, step, islice_=islice):
        if stop and step:
            return lambda x: islice_(x, start, stop, step)
        elif stop:
            return lambda x: islice_(x, start, stop)
        return lambda x: islice_(x, start)
