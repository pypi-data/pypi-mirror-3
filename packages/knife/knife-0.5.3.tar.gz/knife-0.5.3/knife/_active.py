# -*- coding: utf-8 -*-
'''active knives'''

from threading import local
from collections import deque
from contextlib import contextmanager

from stuf.utils import clsname

from knife._compat import loads, optimize


class _ActiveMixin(local):

    '''active knife mixin'''

    def __init__(self, *things, **kw):
        '''
        :argument things: incoming things

        :keyword integer snapshots: snapshots to keep (default: ``5``)
        '''
        incoming = deque()
        incoming.extend(things)
        super(_ActiveMixin, self).__init__(incoming, deque(), **kw)
        # working things
        self._work = deque()
        # holding things
        self._hold = deque()

    @property
    @contextmanager
    def _chain(self, d=optimize):
        # take snapshot
        snapshot = d(self._in)
        # rebalance incoming with outcoming
        if self._history:
            self._in.clear()
            self._in.extend(self._out)
        # make snapshot original snapshot?
        else:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # move incoming things to working things
        self._work.extend(self._in)
        yield
        out = self._out
        # clear outgoing things
        out.clear()
        # extend outgoing things with holding things
        out.extend(self._hold)
        # clear working things
        self._work.clear()
        # clear holding things
        self._hold.clear()

    @property
    def _iterable(self):
        # derived from Raymond Hettinger Python Cookbook recipe # 577155
        call = self._work.popleft
        try:
            while 1:
                yield call()
        except IndexError:
            pass

    def _append(self, thing):
        # append thing after other holding things
        self._hold.append(thing)
        return self

    def _xtend(self, things):
        # place things after holding things
        self._hold.extend(things)
        return self

    def _prependit(self, things, d=optimize):
        # take snapshot
        snapshot = d(self._in)
        # make snapshot original snapshot?
        if self._original is None:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # place thing before other holding things
        self._in.extendleft(reversed(things))
        return self

    def _appendit(self, things, d=optimize):
        # take snapshot
        snapshot = d(self._in)
        # make snapshot original snapshot?
        if self._original is None:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # place things after other incoming things
        self._in.extend(things)
        return self

    def _pipeit(self, knife):
        knife.clear()
        knife._history.clear()
        knife._history.extend(self._history)
        knife._original = self._original
        knife._baseline = self._baseline
        knife._out.extend(self._out)
        knife._worker = self._worker
        knife._args = self._args
        knife._kw = self._kw
        knife._wrapper = self._wrapper
        knife._pipe = self
        return knife

    def _unpipeit(self):
        piped = self._pipe
        piped.clear()
        piped._history.clear()
        piped._history.extend(self._history)
        piped._original = self._original
        piped._baseline = self._baseline
        piped._out.extend(self._out)
        piped._worker = self._worker
        piped._args = self._args
        piped._kw = self._kw
        piped._wrapper = self._wrapper
        self.clear()
        return piped

    def _repr(self, clsname_=clsname, list_=list):
        # object representation
        return self._REPR.format(
            self.__module__,
            clsname_(self),
            list_(self._in),
            list_(self._work),
            list_(self._hold),
            list_(self._out),
        )

    def _len(self, len=len):
        # length of incoming things
        return len(self._in)


class _OutMixin(_ActiveMixin):

    '''active output mixin'''

    def _undo(self, snapshot=0, loads_=loads):
        # clear everything
        self.clear()
        # if specified, use a specific snapshot
        if snapshot:
            self._history.rotate(-(snapshot - 1))
        self._in.extend(loads_(self._history.popleft()))
        return self

    def _snapshot(self, d=optimize):
        # take baseline snapshot of incoming things
        self._baseline = d(self._in)
        return self

    def _rollback(self, loads_=loads):
        # clear everything
        self.clear()
        # clear snapshots
        self._clearsp()
        # revert to baseline snapshot of incoming things
        self._in.extend(loads_(self._baseline))
        return self

    def _revert(self, loads_=loads):
        # clear everything
        self.clear()
        # clear snapshots
        self._clearsp()
        # clear baseline
        self._baseline = None
        # restore original snapshot of incoming things
        self._in.extend(loads_(self._original))
        return self

    def _clear(self, list_=list):
        # clear worker
        self._worker = None
        # clear worker positional arguments
        self._args = ()
        # clear worker keyword arguments
        self._kw = {}
        # default iterable wrapper
        self._wrapper = list_
        # clear pipe
        self._pipe = None
        # clear incoming things
        self._in.clear()
        # clear working things
        self._work.clear()
        # clear holding things
        self._hold.clear()
        # clear outgoing things
        self._out.clear()
        return self

    def _iterate(self, iter_=iter):
        return iter_(self._out)

    def _peek(self, len_=len, list_=list):
        wrap, out = self._wrapper, self._in
        value = list_(wrap(i) for i in out) if self._each else wrap(out)
        self._each = False
        self._wrapper = list_
        return value[0] if len_(value) == 1 else value

    def _get(self, len_=len, list_=list):
        wrap, out = self._wrapper, self._out
        value = list_(wrap(i) for i in out) if self._each else wrap(out)
        self._each = False
        self._wrapper = list_
        return value[0] if len_(value) == 1 else value
