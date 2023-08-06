# -*- coding: utf-8 -*-
'''Lazier evaluated knives.'''

from knife.base import OutMixin
from knife.mixins import (
    RepeatMixin, MapMixin, SliceMixin, ReduceMixin, FilterMixin, MathMixin,
    CmpMixin, OrderMixin)

from knife._lazy import _OutMixin
from knife._base import SLOTS, _KnifeMixin
from knife._mixins import (
    _RepeatMixin, _MapMixin, _SliceMixin, _ReduceMixin, _FilterMixin,
    _MathMixin, _CmpMixin, _OrderMixin)


class lazyknife(
    _OutMixin, _KnifeMixin, _CmpMixin, _FilterMixin, _MapMixin,
    _MathMixin, _OrderMixin, _ReduceMixin, _SliceMixin, _RepeatMixin,
    OutMixin, FilterMixin, MapMixin, ReduceMixin, OrderMixin, RepeatMixin,
    MathMixin, SliceMixin, CmpMixin,
):

    '''
    Lazier evaluated combo knife. Features every :mod:`knife` method.

    .. note::

      Also aliased as :class:`~knife.__` when imported from :mod:`knife`.

    >>> from knife import __
    '''

    __slots__ = SLOTS


class cmpknife(_OutMixin, _KnifeMixin, OutMixin, CmpMixin, _CmpMixin):

    '''
    Lazier evaluated comparing knife. Provides comparison operations for
    incoming things.

    >>> from knife.lazy import cmpknife
    '''

    __slots__ = SLOTS


class filterknife(_OutMixin, _KnifeMixin, OutMixin, FilterMixin, _FilterMixin):

    '''
    Lazier evaluated filtering knife. Provides filtering operations for
    incoming things.

    >>> from knife.lazy import filterknife
    '''

    __slots__ = SLOTS


class mapknife(_OutMixin, _KnifeMixin, OutMixin, MapMixin, _MapMixin):

    '''
    Lazier evaluated mapping knife. Provides `mapping <http://docs.python.org
    /library/functions.html#map>`_ operations for incoming things.

    >>> from knife.lazy import mapknife
    '''

    __slots__ = SLOTS


class mathknife(_OutMixin, _KnifeMixin, OutMixin, MathMixin, _MathMixin):

    '''
    Lazier evaluated mathing knife. Provides numeric and statistical
    operations for incoming things.

    >>> from knife.lazy import mathknife
    '''

    __slots__ = SLOTS


class orderknife(_OutMixin, _KnifeMixin, OutMixin, OrderMixin, _OrderMixin):

    '''
    Lazier evaluated ordering knife. Provides sorting and grouping operations
    for incoming things.

    >>> from knife.lazy import orderknife
    '''

    __slots__ = SLOTS


class reduceknife(_OutMixin, _KnifeMixin, OutMixin, ReduceMixin, _ReduceMixin):

    '''
    Lazier evaluated reducing knife. Provides `reducing <http://docs.python.
    org/library/functions.html#map>`_ operations for incoming things.

    >>> from knife.lazy import reduceknife
    '''

    __slots__ = SLOTS


class repeatknife(_OutMixin, _KnifeMixin, OutMixin, RepeatMixin, _RepeatMixin):

    '''
    Lazier evaluated repeating knife. Provides repetition operations for
    incoming things.

    >>> from knife.lazy import repeatknife
    '''

    __slots__ = SLOTS


class sliceknife(_OutMixin, _KnifeMixin, OutMixin, SliceMixin, _SliceMixin):

    '''
    Lazier evaluated slicing knife. Provides `slicing <http://docs.python.
    org/library/functions.html#slice>`_ operations for incoming things.

    >>> from knife.lazy import sliceknife
    '''

    __slots__ = SLOTS
