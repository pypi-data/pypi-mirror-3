# -*- coding: utf-8 -*-
'''base base knife mixins'''

from operator import truth
from threading import local
from collections import deque

from stuf.utils import memoize
from stuf.patterns import searcher

SLOTS = (
    '_in _work _hold _out _original _baseline _each _kw _history _worker '
    '_wrapper _args _pipe'
).split()


class _KnifeMixin(local):

    '''Base knife mixin.'''

    def __init__(self, ins, outs, **kw):
        super(_KnifeMixin, self).__init__()
        # incoming things
        self._in = ins
        # outgoing things
        self._out = outs
        # pipe out default
        self._pipe = None
        # default output default
        self._each = False
        # original and baseline snapshots
        self._original = self._baseline = None
        # maximum number of history snapshots to keep (default: 5)
        self._history = deque(maxlen=kw.pop('snapshots', 5))
        # worker default
        self._worker = None
        # position arguments default
        self._args = ()
        # keyword arguments default
        self._kw = {}
        # default wrapper default
        self._wrapper = list

    @property
    def _identity(self):
        # use  generic identity function for worker if no worker assigned
        return self._worker if self._worker is not None else lambda x: x

    @property
    def _test(self, truth_=truth):
        # use truth operator function for worker if no worker assigned
        return self._worker if self._worker is not None else truth_

    @staticmethod
    @memoize
    def _pattern(pat, type, flags, s=searcher):
        # compile glob pattern into regex
        return s((type, pat))

    _REPR = '{0}.{1} ([IN: ({2}) => WORK: ({3}) => HOLD: ({4}) => OUT: ({5})])'

    def _clearsp(self):
        # clear fetch snapshots
        self._history.clear()
        return self
