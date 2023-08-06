# -*- coding: utf-8 -*-
'''lazily evaluated knives'''

from threading import local
from itertools import tee, chain
from contextlib import contextmanager

from stuf.deep import clsname
from stuf.iterable import count


class _LazyMixin(local):

    '''lazy knife mixin'''

    def __init__(self, *things, **kw):
        '''
        :argument things: incoming things
        :keyword integer snapshots: snapshots to keep (default: ``5``)
        '''
        incoming = (
            (things[0],).__iter__() if len(things) == 1 else things.__iter__()
        )
        super(_LazyMixin, self).__init__(incoming, ().__iter__(), **kw)
        # working things
        self._work = ().__iter__()
        # holding things
        self._hold = ().__iter__()

    @property
    @contextmanager
    def _chain(self, tee_=tee):
        # take snapshot
        self._in, snapshot = tee_(self._in)
        # rebalance incoming with outcoming
        if self._history:
            self._in, self._out = tee_(self._out)
        # make snapshot original snapshot?
        else:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # move incoming things to working things
        work, self._in = tee_(self._in)
        self._work = work
        yield
        # extend outgoing things with holding things
        self._out = self._hold
        # clear working things
        del self._work
        self._work = ().__iter__()
        # clear holding things
        del self._hold
        self._hold = ().__iter__()

    @property
    def _iterable(self):
        # iterable derived from link in chain
        return self._work

    def _xtend(self, things, chain_=chain):
        # place things after holding things
        self._hold = chain_(things, self._hold)
        return self

    def _append(self, things, chain_=chain):
        # append thing after other holding things
        self._hold = chain_(self._hold, (things,).__iter__())
        return self

    def _prependit(self, things, tee_=tee, chain_=chain):
        # take snapshot
        self._in, snapshot = tee_(self._in)
        # make snapshot original snapshot?
        if self._original is None:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # place things before other incoming things
        self._in = chain_(things, self._in)
        return self

    def _appendit(self, things, tee_=tee, chain_=chain):
        # take snapshot
        self._in, snapshot = tee_(self._in)
        # make snapshot original snapshot?
        if self._original is None:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # place things before other incoming things
        self._in = chain_(self._in, things)
        return self

    def _pipeit(self, knife):
        knife.clear()
        knife._history.clear()
        knife._history.extend(self._history)
        knife._original = self._original
        knife._baseline = self._baseline
        knife._out = self._out
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
        piped._out = self._out
        piped._worker = self._worker
        piped._args = self._args
        piped._kw = self._kw
        piped._wrapper = self._wrapper
        return piped

    def _repr(self, tee_=tee, l=list, clsname_=clsname):
        # object representation
        self._in, in2 = tee_(self._in)
        self._out, out2 = tee_(self._out)
        self._work, work2 = tee_(self._work)
        self._hold, hold2 = tee_(self._hold)
        return self._REPR.format(
            self.__module__,
            clsname_(self),
            l(in2),
            l(work2),
            l(hold2),
            l(out2),
        )

    def _len(self, tee_=tee, count_=count):
        # length of incoming things
        self._in, incoming = tee_(self._in)
        return count_(incoming)


class _OutMixin(_LazyMixin):

    '''lazy output mixin'''

    def _undo(self, snapshot=0):
        # clear everything
        self.clear()
        # if specified, use a specific snapshot
        if snapshot:
            self._history.rotate(-(snapshot - 1))
        self._in = self._history.popleft()
        # clear outgoing things
        del self._out
        self._out = ().__iter__()
        return self

    def _snapshot(self, tee_=tee):
        # take baseline snapshot of incoming things
        self._in, self._baseline = tee_(self._in)
        return self

    def _rollback(self, tee_=tee):
        # clear everything
        self.clear()
        # clear snapshots
        self._clearsp()
        # revert to baseline snapshot of incoming things
        self._in, self._baseline = tee_(self._baseline)
        return self

    def _revert(self, tee_=tee):
        # clear everything
        self.clear()
        # clear snapshots
        self._clearsp()
        # clear baseline
        self._baseline = None
        # restore original snapshot of incoming things
        self._in, self._original = tee_(self._original)
        return self

    def _clear(self, list_=list):
        # clear worker
        self._worker = None
        # clear worker positional arguments
        self._args = ()
        # clear worker keyword arguments
        self._kw = {}
        # revert to default iterable wrapper
        self._wrapper = list_
        # clear pipe
        self._pipe = None
        # clear incoming things
        del self._in
        self._in = ().__iter__()
        # clear working things
        del self._work
        self._work = ().__iter__()
        # clear holding things
        del self._hold
        self._hold = ().__iter__()
        # clear outgoing things
        del self._out
        self._out = ().__iter__()
        return self

    def _iterate(self, tee_=tee):
        self._out, outs = tee_(self._out)
        return outs

    def _peek(self, tee_=tee, list_=list, count_=count):
        tell, self._in, out = tee_(self._in, 3)
        wrap = self._wrapper
        value = list_(wrap(i) for i in out) if self._each else wrap(out)
        # reset each flag
        self._each = False
        # reset wrapper
        self._wrapper = list_
        return value[0] if count_(tell) == 1 else value

    def _get(self, tee_=tee, list_=list, count_=count):
        tell, self._out, out = tee_(self._out, 3)
        wrap = self._wrapper
        value = list_(wrap(i) for i in out) if self._each else wrap(out)
        # reset each flag
        self._each = False
        # reset wrapper
        self._wrapper = list_
        return value[0] if count_(tell) == 1 else value
