# -*- coding: utf-8 -*-
'''base base knife mixins'''

from operator import truth
from threading import local
from collections import deque
from fnmatch import translate
from re import compile as rcompile

from stuf.six import map
from parse import compile as pcompile

from knife._compat import memoize

SLOTS = [
     '_in', '_work', '_hold', '_out', '_original', '_baseline', '_each', '_kw',
     '_history', '_worker', '_wrapper', '_args', '_pipe',
]


class _KnifeMixin(local):

    '''base knife mixin'''

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
    def _pattern(pat, type, flag, t=translate, r=rcompile, p=pcompile):
        # compile glob pattern into regex
        if type == 'glob':
            pat = t(pat)
            type = 'regex'
        return r(pat, flag).search if type == 'regex' else p(pat).search

    def _iter(self, call, iter_=iter, _imap=map):
        # extend fetch with incoming things if knifing them as one thing
        return self._xtend(iter_(call(self._iterable)))

    def _one(self, call, _imap=map):
        # append incoming things to fetch if knifing them as one thing
        return self._append(call(self._iterable))

    def _many(self, call, _imap=map):
        # extend fetch with incoming things if knifing them as one thing
        return self._xtend(call(self._iterable))

    _REPR = '{0}.{1} ([IN: ({2}) => WORK: ({3}) => HOLD: ({4}) => OUT: ({5})])'

    def _clearsp(self):
        # clear fetch snapshots
        self._history.clear()
        return self
