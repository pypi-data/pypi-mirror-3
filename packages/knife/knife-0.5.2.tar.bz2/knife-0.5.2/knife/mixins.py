# -*- coding: utf-8 -*-
'''knife mixins'''

from threading import local


class CmpMixin(local):

    '''
    comparing knife mixin
    '''

    def all(self):
        '''
        Discover if :meth:`worker` is :const:`True` for **every** incoming
        thing.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from knife import __
        >>> __(2, 4, 6, 8).worker(lambda x: x % 2 == 0).all().get()
        True
        '''
        with self._chain:
            return self._one(self._all(self._test))

    def any(self):
        '''
        Discover if :meth:`worker` is :const:`True` for **any** incoming thing.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(1, 4, 5, 9).worker(lambda x: x % 2 == 0).any().get()
        True
        '''
        with self._chain:
            return self._one(self._any(self._test))

    def difference(self, symmetric=False):
        '''
        Discover `difference <http://docs.python.org/library/stdtypes.html#
        set.difference>`_ within a series of `iterable <http://docs.python.
        org/glossary.html#term-iterable>`_ incoming things.

        :keyword boolean symmetric: use `symmetric <http://docs.python.org/
          library/stdtypes.html#set.symmetric_difference>`_ difference

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # default behavior
        >>> test = __([1, 2, 3, 4, 5], [5, 2, 10], [10, 11, 2])
        >>> test.difference().get()
        [1, 3, 4]
        >>> # symmetric difference
        >>> test.original().difference(symmetric=True).get()
        [1, 2, 3, 4, 11]
        '''
        with self._chain:
            return self._many(self._difference(symmetric))

    def intersection(self):
        '''
        Discover `intersection <http://docs.python.org/library/stdtypes.html#
        set.intersection>`_ within a series of `iterable <http://docs.python.
        org/glossary.html#term-iterable>`_ incoming things.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __([1, 2, 3], [101, 2, 1, 10], [2, 1]).intersection().get()
        [1, 2]
        '''
        with self._chain:
            return self._many(self._intersection)

    def union(self):
        '''
        Discover `union <http://docs.python.org/py3k/library/stdtypes.html#
        set.union>`_ within a series of `iterable <http://docs.python.org/
        glossary.html#term-iterable>`_ incoming things.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __([1, 2, 3], [101, 2, 1, 10], [2, 1]).union().get()
        [1, 10, 3, 2, 101]
        '''
        with self._chain:
            return self._many(self._union)

    def unique(self):
        '''
        Discover unique incoming things.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # default behavior
        >>> __(1, 2, 1, 3, 1, 4).unique().get()
        [1, 2, 3, 4]
        >>> # using worker as key function
        >>> __(1, 2, 1, 3, 1, 4).worker(round).unique().get()
        [1, 2, 3, 4]
        '''
        with self._chain:
            return self._iter(self._unique(self._identity))


class MathMixin(local):

    '''mathing knife mixin'''

    def average(self):
        '''
        Discover average value among incoming things.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from knife import __
        >>> __(10, 40, 45).average().get()
        31.666666666666668
        '''
        with self._chain:
            return self._iter(self._average)

    def count(self):
        '''
        Discover how common each incoming thing is.

        Collects :class:`tuple` of
        (*least common thing*, *most common thing*, [*counts of everything*
        (a :class:`list` of :class:`tuple` pairs of (*thing*, *count*))]).

        :rtype: :const:`self` (:obj:`knife` object)

        >>> common = __(11, 3, 5, 11, 7, 3, 5, 11).count().get()
        >>> # least common thing
        >>> common.least
        7
        >>> # most common thing
        >>> common.most
        11
        >>> # total count for every thing
        >>> common.overall
        [(11, 3), (3, 2), (5, 2), (7, 1)]
        '''
        with self._chain:
            return self._iter(self._count)

    def max(self):
        '''
        Discover maximum value among incoming things using :meth:`worker` as
        the `key function <http://docs.python.org/glossary.html#term-key-
        function>`_.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # default behavior
        >>> __(1, 2, 4).max().get()
        4
        >>> stooges = (
        ...    {'name': 'moe', 'age': 40},
        ...    {'name': 'larry', 'age': 50},
        ...    {'name': 'curly', 'age': 60},
        ... )
        >>> # using worker as key function
        >>> __(*stooges).worker(lambda x: x['age']).max().get()
        {'age': 60, 'name': 'curly'}
        '''
        with self._chain:
            return self._iter(self._max(self._identity))

    def median(self):
        '''
        Discover median value among incoming things.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(4, 5, 7, 2, 1).median().get()
        4
        >>> __(4, 5, 7, 2, 1, 8).median().get()
        4.5
        '''
        with self._chain:
            return self._iter(self._median)

    def min(self):
        '''
        Discover minimum value among incoming things using :meth:`worker` as
        the `key function <http://docs.python.org/glossary.html#term-key-
        function>`_.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> test = __(10, 5, 100, 2, 1000)
        >>> test.min().get()
        2
        >>> test.original().worker(lambda x: x % 100 == 0).min().get()
        10
        '''
        with self._chain:
            return self._iter(self._min(self._identity))

    def minmax(self):
        '''
        Discover minimum and maximum values among incoming things.

        Collects :class:`namedtuple` (*minimum value*, *maximum value*).

        :rtype: :const:`self` (:obj:`knife` object)

        >>> minmax = __(1, 2, 4).minmax().get()
        >>> minmax.min
        1
        >>> minmax.max
        4
        '''
        with self._chain:
            return self._iter(self._minmax)

    def range(self):
        '''
        Discover length of the smallest interval that can contain the value of
        every incoming thing.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(3, 5, 7, 3, 11).range().get()
        8
        '''
        with self._chain:
            return self._iter(self._range)

    def sum(self, start=0, precision=False):
        '''
        Discover total value of adding `start` and incoming things together.

        :keyword start: starting number
        :type start: integer or float

        :keyword boolean precision: add floats with extended precision

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # default behavior
        >>> __(1, 2, 3).sum().get()
        6
        >>> # with a starting mumber
        >>> __(1, 2, 3).sum(start=1).get()
        7
        >>> # add floating points with extended precision
        >>> __(.1, .1, .1, .1, .1, .1, .1, .1).sum(precision=True).get()
        0.8
        '''
        with self._chain:
            return self._iter(self._sum(start, precision))


class OrderMixin(local):

    '''ordering knife mixin'''

    def group(self):
        '''
        Group incoming things using :meth:`worker` as the `key function
        <http://docs.python.org/glossary.html#term-key-function>`_.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from knife import __
        >>> # default grouping
        >>> __(1.3, 2.1).group().get()
        [Group(keys=1.3, groups=(1.3,)), Group(keys=2.1, groups=(2.1,))]
        >>> from math import floor
        >>> # use worker for key function
        >>> __(1.3, 2.1, 2.4).worker(floor).group().get()
        [Group(keys=1.0, groups=(1.3,)), Group(keys=2.0, groups=(2.1, 2.4))]
        '''
        with self._chain:
            return self._many(self._group(self._identity))

    def reverse(self):
        '''
        Reverse the order of incoming things.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(5, 4, 3, 2, 1).reverse().get()
        [1, 2, 3, 4, 5]
        '''
        with self._chain:
            return self._many(self._reverse)

    def shuffle(self):
        '''
        Randomly sort incoming things.

        :rtype: :const:`self` (:obj:`knife` object)

          >>> __(5, 4, 3, 2, 1).shuffle().get() # doctest: +SKIP
          [3, 1, 5, 4, 2]
        '''
        with self._chain:
            return self._iter(self._shuffle)

    def sort(self):
        '''
        Reorder incoming things using :meth:`worker` as the `key function
        <http://docs.python.org/glossary.html#term-key-function>`_.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # default sort
        >>> __(4, 6, 65, 3, 63, 2, 4).sort().get()
        [2, 3, 4, 4, 6, 63, 65]
        >>> from math import sin
        >>> # using worker as key function
        >>> __(1, 2, 3, 4, 5, 6).worker(sin).sort().get()
        [5, 4, 6, 3, 1, 2]
        '''
        with self._chain:
            return self._iter(self._sort(self._identity))


class RepeatMixin(local):

    '''repeating knife mixin'''

    def combinate(self, n):
        '''
        Discover `combinations <https://en.wikipedia.org/wiki/Combination>`_
        for every `n` incoming things.

        :argument integer n: number of incoming things to generate
          combinations from

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from knife import __
        >>> __(40, 50, 60).combinate(2).get()
        [(40, 50), (40, 60), (50, 60)]
        '''
        with self._chain:
            return self._many(self._combinations(n))

    def copy(self):
        '''
        Duplicate (by deep copying) each incoming thing.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __([[1, [2, 3]], [4, [5, 6]]]).copy().get()
        [[1, [2, 3]], [4, [5, 6]]]
        '''
        with self._chain:
            return self._many(self._copy)

    def permutate(self, n):
        '''
        Discover `permutations <https://en.wikipedia.org/wiki/Permutation>`_
        for every `n` incoming things.

        :argument integer n: number of incoming things to generate
          permutations from

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(40, 50, 60).permutate(2).get()
        [(40, 50), (40, 60), (50, 40), (50, 60), (60, 40), (60, 50)]
        '''
        with self._chain:
            return self._many(self._permutations(n))

    def repeat(self, n=None, call=False):
        '''
        Repeat either incoming things or invoke :meth:`worker` `n` times.

        :keyword integer n: number of times to repeat

        :keyword boolean call: repeat results of invoking :meth:`worker`

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # repeat iterable
        >>> __(40, 50, 60).repeat(3).get()
        [(40, 50, 60), (40, 50, 60), (40, 50, 60)]
        >>> def test(*args):
        ...    return list(args)
        >>> # with worker
        >>> __(40, 50, 60).worker(test).repeat(n=3, call=True).get()
        [[40, 50, 60], [40, 50, 60], [40, 50, 60]]
        '''
        with self._chain:
            return self._many(self._repeat(n, call, self._identity))


class MapMixin(local):

    '''mapping knife mixin'''

    def argmap(self, merge=False):
        '''
        Feed each incoming thing to :meth:`worker` as `wildcard <http://docs.
        python.org/reference/compound_stmts.html#function>`_ `positional
        arguments <http://docs.python.org/glossary.html#term-positional-
        argument>`_.

        :keyword boolean merge: merge global positional :meth:`params` with
          positional arguments derived from incoming things

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from knife import __
        >>> # default behavior
        >>> test = __((1, 2), (2, 3), (3, 4))
        >>> test.worker(lambda x, y: x * y).argmap().get()
        [2, 6, 12]
        >>> # merge global positional arguments with iterable arguments
        >>> test.original().worker(
        ...   lambda x, y, z, a, b: x * y * z * a * b
        ... ).params(7, 8, 9).argmap(merge=True).get()
        [1008, 3024, 6048]
        '''
        with self._chain:
            return self._many(self._argmap(self._worker, merge, self._args))

    def invoke(self, name):
        '''
        Call method `name` from each incoming thing with the global `positional
        <http://docs.python.org/glossary.html#term-positional-argument>`_ and
        `keyword <http://docs.python.org/glossary.html#term-keyword-argument>`_
        :meth:`params`.

        The original thing is kept if the return value of the method call is
        :const:`None`.

        :argument string name: method name

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # invoke list.index()
        >>> __([5, 1, 7], [3, 2, 1]).params(1).invoke('index').get()
        [1, 2]
        >>> # invoke list.sort() but return sorted list instead of None
        >>> __([5, 1, 7], [3, 2, 1]).invoke('sort').get()
        [[1, 5, 7], [1, 2, 3]]
        '''
        with self._chain:
            return self._many(self._invoke(name, (self._args, self._kw)))

    def kwargmap(self, merge=False):
        '''
        Feed each incoming thing as a :class:`tuple` of `wildcard <http://docs.
        python.org/reference/compound_stmts.html#function>`_ `positional <http:
        //docs.python.org/glossary.html#term-positional-argument>`_ and
        `keyword <http://docs.python.org/glossary.html#term-keyword-argument>`_
        arguments to :meth:`worker`.

        :keyword boolean merge: merge global positional or keyword
          :meth:`params` with positional and keyword arguments derived from an
          incoming things into a single :class:`tuple` of wildcard positional
          and keyword arguments like (*iterable_args* + *global_args*,
          *global_kwargs* + *iterable_kwargs*)

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # default behavior
        >>> test = __(
        ...  ((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})
        ... )
        >>> def tester(*args, **kw):
        ...    return sum(args) * sum(kw.values())
        >>> test.worker(tester).kwargmap().get()
        [6, 10, 14]
        >>> # merging global and iterable derived positional and keyword args
        >>> test.original().worker(tester).params(
        ...   1, 2, 3, b=5, w=10, y=13
        ... ).kwargmap(merge=True).get()
        [270, 330, 390]
        '''
        with self._chain:
            return self._many(self._kwargmap(
                self._worker, merge, self._args, self._kw,
            ))

    def map(self):
        '''
        Feed each incoming thing to :meth:`worker`.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(1, 2, 3).worker(lambda x: x * 3).map().get()
        [3, 6, 9]
        '''
        with self._chain:
            return self._many(self._map(self._worker))

    def mapping(self, keys=False, values=False):
        '''
        Run :meth:`worker` on incoming `mapping <http://docs.python.org/
        glossary.html#term-mapping>`_ things.

        :keyword boolean keys: collect mapping keys only

        :keyword boolean values: collect mapping values only

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # filter items
        >>> __(dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
        ... ).worker(lambda x, y: x * y).mapping().get()
        [2, 6, 12, 2, 6, 12]
        >>> # mapping keys only
        >>> __(dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
        ... ).mapping(keys=True).get()
        [1, 2, 3, 1, 2, 3]
        >>> # mapping values only
        >>> __(dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
        ... ).mapping(values=True).get()
        [2, 3, 4, 2, 3, 4]
        '''
        with self._chain:
            return self._many(self._mapping(self._identity, keys, values))


class FilterMixin(local):

    '''filtering knife mixin'''

    def attrs(self, *names):
        '''
        Collect `attribute <http://docs.python.org/glossary.html#term-
        attribute>`_ values from incoming things that match an attribute *name*
        found in `names`.

        :argument string names: attribute names

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from knife import __
        >>> from stuf import stuf
        >>> stooge = [
        ...    stuf(name='moe', age=40),
        ...    stuf(name='larry', age=50),
        ...    stuf(name='curly', age=60),
        ... ]
        >>> __(*stooge).attrs('name').get()
        ['moe', 'larry', 'curly']
        >>> # multiple attribute names
        >>> __(*stooge).attrs('name', 'age').get()
        [('moe', 40), ('larry', 50), ('curly', 60)]
        >>> # no attrs named 'place'
        >>> __(*stooge).attrs('place').get()
        []
        '''
        with self._chain:
            return self._iter(self._attributes(names))

    def duality(self):
        '''
        Divide incoming things into two `iterables <http://docs.python.org/
        glossary.html#term-iterable>`_, the first everything :meth:`worker` is
        :const:`True` for and the second everything :meth:`worker` is
        :const:`False` for.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> test = __(1, 2, 3, 4, 5, 6).worker(lambda x: x % 2 == 0)
        >>> divide = test.duality().get()
        >>> divide.true
        (2, 4, 6)
        >>> divide.false
        (1, 3, 5)
        '''
        with self._chain:
            return self._iter(self._duality(self._test))

    def filter(self, invert=False):
        '''
        Collect incoming things matched by :meth:`worker`.

        :keyword boolean invert: collect things :meth:`worker` is
          :const:`False` rather than :const:`True` for

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # filter for true values
        >>> test = __(1, 2, 3, 4, 5, 6).worker(lambda x: x % 2 == 0)
        >>> test.filter().get()
        [2, 4, 6]
        >>> # filter for false values
        >>> test.original().worker(
        ...   lambda x: x % 2 == 0
        ... ).filter(invert=True).get()
        [1, 3, 5]
        '''
        with self._chain:
            return self._many(self._filter(self._test, invert))

    def items(self, *keys):
        '''
        Collect values from incoming things (usually `sequences <http://docs.
        python.org/glossary.html#term-sequence>`_ or `mappings <http://docs.
        python.org/glossary.html#term-mapping>`_) that match a *key* found in
        `keys`.

        :argument string keys: keys or indices

        :rtype: :const:`self` (:obj:`knife` object)

        >>> stooge = [
        ...    dict(name='moe', age=40),
        ...    dict(name='larry', age=50),
        ...    dict(name='curly', age=60)
        ... ]
        >>> # get items from mappings like dictionaries, etc...
        >>> __(*stooge).items('name').get()
        ['moe', 'larry', 'curly']
        >>> __(*stooge).items('name', 'age').get()
        [('moe', 40), ('larry', 50), ('curly', 60)]
        >>> # get items from sequences like lists, tuples, etc...
        >>> stooge = [['moe', 40], ['larry', 50], ['curly', 60]]
        >>> __(*stooge).items(0).get()
        ['moe', 'larry', 'curly']
        >>> __(*stooge).items(1).get()
        [40, 50, 60]
        >>> __(*stooge).items('place').get()
        []
        '''
        with self._chain:
            return self._iter(self._items(keys))

    def traverse(self, invert=False):
        '''
        Collect deeply nested values from incoming things matched by
        :meth:`worker`.

        :keyword boolean invert: collect things that :meth:`worker` is
          :const:`False` rather than :const:`True` for

        :rtype: :const:`self` (:obj:`knife` object)

        >>> class stooge:
        ...    name = 'moe'
        ...    age = 40
        >>> class stooge2:
        ...    name = 'larry'
        ...    age = 50
        >>> class stooge3:
        ...    name = 'curly'
        ...    age = 60
        ...    class stooge4(object):
        ...        name = 'beastly'
        ...        age = 969
        >>> def test(x):
        ...    if x[0] == 'name':
        ...        return True
        ...    elif x[0].startswith('__'):
        ...        return True
        ...    return False
        >>> # using worker while filtering for False values
        >>> __(stooge, stooge2, stooge3).worker(test).traverse(
        ...   invert=True
        ... ).get() # doctest: +NORMALIZE_WHITESPACE
        [ChainMap(OrderedDict([('classname', 'stooge'), ('age', 40)])),
        ChainMap(OrderedDict([('classname', 'stooge2'), ('age', 50)])),
        ChainMap(OrderedDict([('classname', 'stooge3'), ('age', 60)]),
        OrderedDict([('age', 969), ('classname', 'stooge4')]))]
        '''
        with self._chain:
            if self._worker is None:
                test = lambda x: not x[0].startswith('__')
            else:
                test = self._worker
            return self._many(self._traverse(test, invert))


class ReduceMixin(local):

    '''reducing knife mixin'''

    def flatten(self):
        '''
        Reduce nested incoming things to flattened incoming things.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from knife import __
        >>> __([[1, [2], [3, [[4]]]], 'here']).flatten().get()
        [1, 2, 3, 4, 'here']
        '''
        with self._chain:
            return self._many(self._flatten)

    def merge(self):
        '''
        Reduce multiple `iterable
        <http://docs.python.org/glossary.html#term-iterable>`_ incoming
        things into one iterable incoming thing.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(['moe', 'larry'], [30, 40], [True, False]).merge().get()
        ['moe', 'larry', 30, 40, True, False]
        '''
        with self._chain:
            return self._many(self._merge)

    def reduce(self, initial=None, reverse=False):
        '''
        Reduce `iterable <http://docs.python.org/glossary.html#term-iterable>`_
        incoming things down to one incoming thing using :meth:`worker`.

        :rtype: :const:`self` (:obj:`knife` object)

        :keyword initial: starting value

        :keyword boolean reverse: reduce from `the right side
          <http://www.zvon.org/other/haskell/Outputprelude/foldr_f.html>`_
          of incoming things

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # reduce from left side
        >>> __(1, 2, 3).worker(lambda x, y: x + y).reduce().get()
        6
        >>> # reduce from left side with initial value
        >>> __(1, 2, 3).worker(lambda x, y: x + y).reduce(initial=1).get()
        7
        >>> # reduce from right side
        >>> test = __([0, 1], [2, 3], [4, 5]).worker(lambda x, y: x + y)
        >>> test.reduce(reverse=True).get()
        [4, 5, 2, 3, 0, 1]
        >>> # reduce from right side with initial value
        >>> test.original().worker(
        ... lambda x, y: x + y
        ... ).reduce([0, 0], True).get()
        [4, 5, 2, 3, 0, 1, 0, 0]
        '''
        with self._chain:
            return self._one(self._reduce(self._worker, initial, reverse))

    def zip(self):
        '''
        Convert multiple `iterable <http://docs.python.org/glossary.html#
        term-iterable>`_ incoming things to :class:`tuples` composed of things
        found at the same index position within the original iterables.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> test = __(['moe', 'larry'], [30, 40], [True, False])
        >>> test.zip().get()
        [('moe', 30, True), ('larry', 40, False)]
        '''
        with self._chain:
            return self._many(self._zip)


class SliceMixin(local):

    '''slicing knife mixin'''

    def at(self, n, default=None):
        '''
        `Slice <http://docs.python.org/glossary.html#term-slice>`_ off
        incoming thing found at index `n`.

        :argument integer n: index of some incoming thing

        :keyword default: default returned if nothing is found at `n`

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from knife import __
        >>> # default behavior
        >>> __(5, 4, 3, 2, 1).at(2).get()
        3
        >>> # return default value if nothing found at index
        >>> __(5, 4, 3, 2, 1).at(10, 11).get()
        11
        '''
        with self._chain:
            return self._one(self._at(n, default))

    def choice(self):
        '''
        Randomly `slice <http://docs.python.org/glossary.html#term-slice>`_
        off **one** incoming thing.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(1, 2, 3, 4, 5, 6).choice().get() # doctest: +SKIP
        3
        '''
        with self._chain:
            return self._iter(self._choice())

    def dice(self, n, fill=None):
        '''
        `Slice <http://docs.python.org/glossary.html#term-slice>`_ one
        `iterable <http://docs.python.org/glossary.html#term-iterable>`_
        incoming thing into `n` iterable incoming things.

        :argument integer n: number of incoming things per slice

        :keyword fill: value to pad out incomplete iterables

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __('moe', 'larry', 'curly', 30, 40, 50, True).dice(2, 'x').get()
        [('moe', 'larry'), ('curly', 30), (40, 50), (True, 'x')]
        '''
        with self._chain:
            return self._many(self._dice(n, fill))

    def first(self, n=0):
        '''
        Slice off `n` things from the **starting** end of incoming things or
        just the **first** incoming thing.

        :keyword integer n: number of incoming things

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # default behavior
        >>> __(5, 4, 3, 2, 1).first().get()
        5
        >>> # first things from index 0 to 2
        >>> __(5, 4, 3, 2, 1).first(2).get()
        [5, 4]
        '''
        with self._chain:
            return self._iter(self._first(n))

    def initial(self):
        '''
        `Slice <http://docs.python.org/glossary.html#term-slice>`_ off
        everything except the **last** incoming thing.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(5, 4, 3, 2, 1).initial().get()
        [5, 4, 3, 2]
        '''
        with self._chain:
            return self._many(self._initial)

    def last(self, n=0):
        '''
        `Slice <http://docs.python.org/glossary.html#term-slice>`_ off `n`
        things from the **tail** end of incoming things or just the **last**
        incoming thing.

        :keyword integer n: number of incoming things

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # default behavior
        >>> __(5, 4, 3, 2, 1).last().get()
        1
        >>> # fetch last two things
        >>> __(5, 4, 3, 2, 1).last(2).get()
        [2, 1]
        '''
        with self._chain:
            return self._iter(self._last(n))

    def rest(self):
        '''
        `Slice <http://docs.python.org/glossary.html#term-slice>`_ off
        everything except the **first** incoming thing.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(5, 4, 3, 2, 1).rest().get()
        [4, 3, 2, 1]
        '''
        with self._chain:
            return self._many(self._rest)

    def sample(self, n):
        '''
        Randomly `slice <http://docs.python.org/glossary.html#term-slice>`_ off
        `n` incoming things.

        :argument integer n: sample size

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(1, 2, 3, 4, 5, 6).sample(3).get() # doctest: +SKIP
        [2, 4, 5]
        '''
        with self._chain:
            return self._iter(self._sample(n))

    def slice(self, start, stop=False, step=False):
        '''
        Take a `slice <http://docs.python.org/glossary.html#term-slice>`_ out
        of incoming things.

        :argument integer start: starting index of slice

        :keyword integer stop: stopping index of slice

        :keyword integer step: size of step in slice

        :rtype: :const:`self` (:obj:`knife` object)

        >>> # slice from index 0 to 3
        >>> __(5, 4, 3, 2, 1).slice(2).get()
        [5, 4]
        >>> # slice from index 2 to 4
        >>> __(5, 4, 3, 2, 1).slice(2, 4).get()
        [3, 2]
        >>> # slice from index 2 to 4 with 2 steps
        >>> __(5, 4, 3, 2, 1).slice(2, 4, 2).get()
        3
        '''
        with self._chain:
            return self._many(self._slice(start, stop, step))
