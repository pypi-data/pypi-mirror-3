# -*- coding: utf-8 -*-
'''specific knife mixins'''

from math import fsum
from copy import deepcopy
from threading import local
from functools import reduce
from inspect import getmro, isclass
from random import randrange, shuffle
from collections import deque, namedtuple
from operator import attrgetter, itemgetter, methodcaller, truediv
from itertools import (
    chain, combinations, groupby, islice, repeat, permutations, starmap, tee)

from stuf.deep import selfname
from stuf.utils import memoize
from stuf.collects import Counter, ChainMap
from stuf.six.moves import filterfalse, zip_longest  # @UnresolvedImport
from stuf.iterable import deferfunc, deferiter, count
from stuf.six import OrderedDict, filter, items, keys, map, strings, values


Count = namedtuple('Count', 'least most overall')
GroupBy = namedtuple('Group', 'keys groups')
MinMax = namedtuple('MinMax', 'min max')
TrueFalse = namedtuple('TrueFalse', 'true false')


def slicer(x, y, iz=islice, nx=next):
    return nx(iz(x, y, None))


class _CmpMixin(local):

    '''comparing mixin'''

    @memoize
    def _all(self, a=all, m=map):
        # invoke worker on each item to yield truth
        return self._append(a(m(self._test, self._iterable)))

    @memoize
    def _any(self, a=any, m=map):
        # invoke worker on each item to yield truth
        return self._append(a(m(self._test, self._iterable)))

    @memoize
    def _difference(self, symmetric, rz=reduce, se=set):
        if symmetric:
            test = lambda x, y: se(x).symmetric_difference(y)
        else:
            test = lambda x, y: se(x).difference(y)
        return self._xtend(rz(test, self._iterable))

    def _intersection(self, rz=reduce, se=set):
        return self._xtend(
            rz(lambda x, y: se(x).intersection(y), self._iterable)
        )

    def _union(self, rz=reduce, se=set):
        return self._xtend(rz(lambda x, y: se(x).union(y), self._iterable))

    @memoize
    def _unique(self, nx=next, se=set, S=StopIteration):
        def unique(key, iterable):
            seen = se()
            seenadd = seen.add
            try:
                while 1:
                    element = key(nx(iterable))
                    if element not in seen:
                        yield element
                        seenadd(element)
            except S:
                pass
        return self._xtend(unique(self._identity, self._iterable))


class _MathMixin(local):

    '''number mixin'''

    def _average(self, cnt=count, su=sum, td=truediv, t=tee):
        i1, i2 = t(self._iterable)
        return self._append(td(su(i1, 0.0), cnt(i2)))

    def _count(self, R=Counter, T=Count):
        cnt = R(self._iterable).most_common
        commonality = cnt()
        return self._append(T(
            # least common
            commonality[:-2:-1][0][0],
            # most common (mode)
            cnt(1)[0][0],
            # overall commonality
            commonality,
        ))

    @memoize
    def _max(self, mx=max):
        return self._append(mx(self._iterable, key=self._identity))

    def _median(
        self, t=tee, sd=sorted, td=truediv, i=int, cnt=count, z=slicer,
    ):
        i1, i2 = t(sd(self._iterable))
        result = td(cnt(i1) - 1, 2)
        pint = i(result)
        if result % 2 == 0:
            return self._append(z(i2, pint))
        i3, i4 = t(i2)
        return self._append(td(z(i3, pint) + z(i4, pint + 1), 2))

    def _minmax(self, mn=min, mx=max, t=tee, MM=MinMax):
        i1, i2 = t(self._iterable)
        return self._append(MM(mn(i1), mx(i2)))

    def _range(self, d=deque, sd=sorted, nx=next, t=tee):
        i1, i2 = t(sd(self._iterable))
        return self._append(d(i1, maxlen=1).pop() - nx(i2))

    @memoize
    def _min(self, mn=min):
        return self._append(mn(self._iterable, key=self._identity))

    @memoize
    def _sum(self, start, floats, su=sum, fs=fsum):
        return self._append(
            fs(self._iterable) if floats else su(self._iterable, start)
        )


class _OrderMixin(local):

    '''order mixin'''

    @memoize
    def _group(
        self, G=GroupBy, S=StopIteration, g=groupby, nx=next, sd=sorted,
        tu=tuple,
    ):
        def grouper(call, iterable):
            try:
                it = g(sd(iterable, key=call), call)
                while 1:
                    k, v = nx(it)
                    yield G(k, tu(v))
            except S:
                pass
        return self._xtend(grouper(self._identity, self._iterable))

    def _reverse(self, S=StopIteration, nx=next, rv=reversed, tu=tuple):
        return self._xtend(rv(tu(self._iterable)))

    def _shuffle(self, l=list, sf=shuffle):
        iterable = l(self._iterable)
        sf(iterable)
        return self._xtend(iterable)

    @memoize
    def _sort(self, sd=sorted):
        return self._xtend(sd(self._iterable, key=self._identity))


class _RepeatMixin(local):

    '''repetition mixin'''

    def _combinate(self, n, cb=combinations):
        return self._xtend(cb(self._iterable, n))

    def _copy(self, dc=deepcopy, m=map):
        return self._xtend(m(dc, self._iterable))

    def _permute(self, n, pm=permutations):
        return self._xtend(pm(self._iterable, n))

    @memoize
    def _repeat(self, n, use, rt=repeat, sm=starmap, tu=tuple):
        call = self._identity
        if use:
            return self._xtend(sm(call, rt(tu(self._iterable), n)))
        return self._xtend(rt(tu(self._iterable), n))


class _MapMixin(local):

    '''mapping mixin'''

    @memoize
    def _argmap(self, curr, sm=starmap):
        call = self._worker
        if curr:
            def argmap(*args):
                return call(*(args + self._args))
            return self._xtend(sm(argmap, self._iterable))
        return self._xtend(sm(call, self._iterable))

    @memoize
    def _invoke(self, name, m=map, mc=methodcaller):
        def invoke(thing, caller=mc(name, *self._args, **self._kw)):
            read = caller(thing)
            return thing if read is None else read
        return self._xtend(m(invoke, self._iterable))

    @memoize
    def _kwargmap(self, curr, sm=starmap):
        call = self._worker
        if curr:
            def kwargmap(*params):
                args, kwargs = params
                kwargs.update(self._kw)
                return call(*(args + self._args), **kwargs)
        else:
            kwargmap = lambda x, y: call(*x, **y)
        return self._xtend(sm(kwargmap, self._iterable))

    @memoize
    def _map(self, m=map):
        return self._xtend(m(self._worker, self._iterable))

    @memoize
    def _mapping(
        self, key, value, ky=keys, it=items, vl=values, sm=starmap,
        m=map, ci=chain.from_iterable,
    ):
        call = self._identity
        if key:
            return self._xtend(m(call, ci(m(ky, self._iterable))))
        elif value:
            return self._xtend(m(call, ci(m(vl, self._iterable))))
        return self._xtend(sm(call, ci(m(it, self._iterable))))


class _FilterMixin(local):

    '''filtering mixin'''

    @memoize
    def _attrs(
        self, names, A=AttributeError, S=StopIteration, ag=attrgetter, nx=next
    ):
        def attrs(iterable, get=ag(*names)):
            try:
                while 1:
                    try:
                        yield get(nx(iterable))
                    except A:
                        pass
            except S:
                pass
        return self._xtend(attrs(self._iterable))

    @memoize
    def _duality(
        self, TF=TrueFalse, f=filter, ff=filterfalse, tu=tuple, t=tee,
    ):
        truth, false = t(self._iterable)
        call = self._test
        return self._append(TF(tu(f(call, truth)), tu(ff(call, false))))

    @memoize
    def _filter(self, false, f=filter, ff=filterfalse):
        return self._xtend((ff if false else f)(self._worker, self._iterable))

    @memoize
    def _items(
        self, key, ig=itemgetter, I=IndexError, K=KeyError, T=TypeError,
        nx=next, S=StopIteration,
    ):
        def itemz(iterable, get=ig(*key)):
            try:
                while 1:
                    try:
                        yield get(nx(iterable))
                    except (I, K, T):
                        pass
            except S:
                pass
        return self._xtend(itemz(self._iterable))

    @memoize
    def _traverse(
        self, invert, CM=ChainMap, O=OrderedDict, S=StopIteration, cn=chain,
        d=dir, f=filter, ff=filterfalse, ga=getattr, gm=getmro, ic=isclass,
        ii=isinstance, nx=next, se=set, sn=selfname, vz=vars,
    ):
        if self._worker is None:
            test = lambda x: not x[0].startswith('__')
        else:
            test = self._worker
        ifilter = ff if invert else f
        def members(iterable, beenthere=None): #@IgnorePep8
            isclass_ = ic
            getattr_ = ga
            o_ = O
            members_ = members
            ifilter_ = ifilter
            varz_ = vz
            test_ = test
            mro = gm(iterable)
            names = d(iterable).__iter__()
            if beenthere is None:
                beenthere = se()
            adder_ = beenthere.add
            try:
                while 1:
                    name = nx(names)
                    # yes, it's really supposed to be a tuple
                    for base in cn([iterable], mro):
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
            except S:
                pass
        def traverse(iterable): #@IgnorePep8
            isinstance_ = ii
            selfname_ = sn
            members_ = members
            o_ = O
            cm_ = CM
            ifilter_ = ifilter
            test_ = test
            try:
                while 1:
                    iterator = nx(iterable)
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
            except S:
                pass
        return self._xtend(traverse(self._iterable))


class _ReduceMixin(local):

    '''reduce mixin'''

    def _flatten(
        self, A=AttributeError, S=StopIteration, T=TypeError, nx=next,
        st=strings, ii=isinstance,
    ):
        def flatten(iterable):
            next_ = iterable.__iter__()
            try:
                while 1:
                    item = nx(next_)
                    try:
                        # don't recur over strings
                        if ii(item, st):
                            yield item
                        else:
                            # do recur over other things
                            for j in flatten(item):
                                yield j
                    except (A, T):
                        # does not recur
                        yield item
            except S:
                pass
        return self._xtend(flatten(self._iterable))

    def _merge(self, ci=chain.from_iterable):
        return self._xtend(ci(self._iterable))

    @memoize
    def _reduce(self, initial, reverse, rz=reduce):
        call = self._worker
        if reverse:
            if initial is None:
                return self._append(
                    rz(lambda x, y: call(y, x), self._iterable)
                )
            return self._append(
                rz(lambda x, y: call(y, x), self._iterable, initial)
            )
        if initial is None:
            return self._append(rz(call, self._iterable))
        return self._append(rz(call, self._iterable, initial))

    def _zip(self, zip_=zip_longest):
        return self._xtend(zip_(*self._iterable))


class _SliceMixin(local):

    '''slicing mixin'''

    @memoize
    def _at(self, n, default, iz=islice, nx=next):
        return self._append(nx(iz(self._iterable, n, None), default))

    @memoize
    def _choice(self, cnt=count, iz=islice, nx=next, rr=randrange, t=tee):
        i1, i2 = t(self._iterable)
        return self._append(iz(i1, rr(0, cnt(i2)), None))

    @memoize
    def _dice(self, n, fill, zl=zip_longest):
        return self._xtend(
            zl(fillvalue=fill, *[self._iterable.__iter__()] * n)
        )

    @memoize
    def _first(self, n=0, df=deferiter, iz=islice):
        return self._xtend(iz(self._iterable, n) if n else df(self._iterable))

    def _initial(self, cnt=count, iz=islice, t=tee):
        i1, i2 = t(self._iterable)
        return self._xtend(iz(i1, cnt(i2) - 1))

    @memoize
    def _last(self, n, cnt=count, d=deque, df=deferfunc, iz=islice, t=tee):
        if n:
            i1, i2 = t(self._iterable)
            return self._xtend(iz(i1, cnt(i2) - n, None))
        return self._xtend(df(d(self._iterable, maxlen=1).pop))

    def _rest(self, iz=islice):
        return self._xtend(iz(self._iterable, 1, None))

    @memoize
    def _sample(self, n, t=tee, z=slice, rr=randrange, m=map, cnt=count):
        i1, i2 = t(self._iterable)
        length = cnt(i1)
        return self._xtend(m(lambda x: z(x, rr(0, length)), t(i2, n)))

    def _slice(self, start, stop, step, iz=islice):
        if stop and step:
            return self._xtend(iz(self._iterable, start, stop, step))
        elif stop:
            return self._xtend(iz(self._iterable, start, stop))
        return self._xtend(iz(self._iterable, start))
