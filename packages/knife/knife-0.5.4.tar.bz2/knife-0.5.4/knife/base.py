# -*- coding: utf-8 -*-
'''base knife mixins'''

from threading import local

from stuf.six import tounicode, tobytes


class KnifeMixin(local):

    '''base knife mixin'''

    def apply(self, worker, *args, **kw):
        '''
        Assign :func:`callable` used to work on incoming things plus any
        :term:`positional argument`\s and :term:`keyword argument`\s
        it will use.

        .. note::

          Global :term:`positional argument`\s and :term:`keyword argument`\s
          assigned with :meth:`params` are reset whenever :func:`apply` is
          called.

        :argument worker: a :func:`callable`

        :rtype: :mod:`knife` :term:`object`
        '''
        # assign worker
        self._worker = worker
        # positional params
        self._args = args
        # keyword arguemnts
        self._kw = kw
        return self

    def worker(self, worker):
        '''
        Assign :func:`callable` used to work on incoming things.

        .. note::

          Global :term:`positional argument`\s and :term:`keyword argument`\s
          assigned with :meth:`params` are reset whenever a new `worker` is
          assigned.

        :argument worker: a :func:`callable`

        :rtype: :mod:`knife` :term:`object`
        '''
        # reset stored position params
        self._args = ()
        # reset stored keyword params
        self._kw = {}
        # assign worker
        self._worker = worker
        return self

    def params(self, *args, **kw):
        '''
        Assign :term:`positional argument`\s and :term:`keyword argument`\s
        to be used globally.

        :rtype: :mod:`knife` :term:`object`
        '''
        # positional params
        self._args = args
        # keyword arguemnts
        self._kw = kw
        return self

    def pattern(self, pattern, type='parse', flags=0):
        '''
        Compile search `pattern` for use as :meth:`worker`.

        .. note::

          Global :term:`positional argument`\s and :term:`keyword argument`\s
          assigned with :meth:`params` are reset whenever a new `pattern` is
          compiled.

        :argument str pattern: search pattern

        :keyword str type: engine to compile `pattern` with. Valid options
          are `'parse' <http://pypi.python.org/pypi/parse/>`_, `'re'
          <http://docs.python.org/library/re.html>`_, or `'glob' <http://docs.
          python.org/library/fnmatch.html>`_

        :keyword int flags: regular expression `flags <http://docs.python.org/
          library/re.html#re.DEBUG>`_

        :rtype: :mod:`knife` :term:`object`

        >>> # using parse expression
        >>> test = __('first test', 'second test', 'third test')
        >>> test.pattern('first {}').filter().get()
        'first test'
        >>> # using glob pattern
        >>> test.original().pattern('second*', type='glob').filter().get()
        'second test'
        >>> # using regular expression
        >>> test.original().pattern('third .', type='regex').filter().get()
        'third test'
        '''
        # reset stored position params
        self._args = ()
        # reset stored keyword params
        self._kw = {}
        self._worker = self._pattern(pattern, type, flags)
        return self

    def prepend(self, *things):
        '''
        Insert `things` **before** other incoming things.

        :argument things: incoming things

        :rtype: :mod:`knife` :term:`object`

        >>> __(3, 4, 5).prepend(1, 2, 3, 4, 5, 6).peek()
        [1, 2, 3, 4, 5, 6, 3, 4, 5]
        '''
        return self._prependit(things)

    def append(self, *things):
        '''
        Insert `things` **after** other incoming things.

        :argument things: incoming things

        :rtype: :mod:`knife` :term:`object`

        >>> from knife import __
        >>> __(3, 4, 5).append(1, 2, 3, 4, 5, 6).peek()
        [3, 4, 5, 1, 2, 3, 4, 5, 6]
        '''
        return self._appendit(things)

    def pipe(self, knife):
        '''
        Pipe incoming things from some other :mod:`knife` :term:`object`
        through this :mod:`knife` :term:`object`.

        :argument knife: another :mod:`knife` :term:`object`

        :rtype: :mod:`knife` :term:`object`
        '''
        with self._chain:
            return self._pipeit(knife)

    def back(self):
        '''
        Switch back to :mod:`knife` :term:`object` that piped its incoming
        things through this :mod:`knife` :term:`object`.

        :rtype: :mod:`knife` :term:`object`
        '''
        with self._chain:
            return self._unpipeit()

    def __len__(self):
        '''Number of incoming things.'''
        return self._len()

    def __repr__(self):
        '''String representation.'''
        return self._repr()


class OutMixin(KnifeMixin):

    '''output mixin'''

    def __iter__(self):
        '''Iterate over outgoing things.'''
        return self._iterate()

    def get(self):
        '''
        Return outgoing things wrapped with :meth:`wrap`.

        .. note::

          With only one outgoing thing, only that one outgoing thing is
          returned. With multiple outgoing things, they are returned wrapped
          with the wrapper assigned with :meth:`wrap` (default wrapper is
          :func:`list`).
        '''
        return self._get()

    def peek(self):
        '''
        Preview current incoming things wrapped with :meth:`wrap`.

        .. note::

          With only one outgoing thing, only that one thing is returned. With
          multiple outgoing things, everything is returned wrapped with the
          wrapper assigned with :meth:`wrap` (default wrapper is :func:`list`).
        '''
        return self._peek()

    def wrap(self, wrapper):
        '''
        Assign :term:`object`, :term:`type`, or :keyword:`class` used to wrap
        outgoing things.

        .. note::

          A :mod:`knife` :term:`object` resets back to its default wrapper
          (:func:`list`) after :meth:`get` or :meth:`peek` is called.

        :argument wrapper: an :term:`object`, :func:`type`, or :keyword:`class`

        :rtype: :mod:`knife` :term:`object`

        >>> __(1, 2, 3, 4, 5, 6).wrap(tuple).peek()
        (1, 2, 3, 4, 5, 6)
        '''
        self._wrapper = wrapper
        return self

    def oneach(self):
        '''
        Toggle whether each outgoing thing should be individually wrapped with
        the wrapper assigned with :meth:`wrap` (default wrapper is :func:`list`
        ) or whether all outgoing things should be wrapped all at once.

        .. note::

          :mod:`knife` :term:`object` default behavior is to wrap all outgoing
          things all at once. :mod:`knife` :term:`object`\s reset back to this
          behavior **after** :meth:`get` or :meth:`peek` is called.

        :rtype: :mod:`knife` :term:`object`
        '''
        self._each = not self._each
        return self

    def ascii(self, errors='strict'):
        '''
        :meth:`~str.encode` outgoing things as `bytes <http://docs.python
        .org/py3k/library/functions.html#bytes>`_ with the ``'latin-1'`` codec.

        :keyword str errors: `error handling <http://docs.python.org/library/
          codecs.html#codec-base-classes>`_ for encoding

        :rtype: :mod:`knife` :term:`object`

        >>> from stuf.six import u, b
        >>> test = __([1], True, r't', b('i'), u('g'), None, (1,))
        >>> test.ascii().oneach().peek()
        ['[1]', 'True', 't', 'i', 'g', 'None', '(1,)']
        '''
        self._wrapper = lambda x: tobytes(x, 'latin_1', errors)
        return self

    def bytes(self, encoding='utf_8', errors='strict'):
        '''
        :meth:`~str.encode` outgoing things as `bytes <http://docs.python
        .org/py3k/library/functions.html#bytes>`_.

        :keyword str encoding: character `encoding <http://docs.python.org/
          library/codecs.html#standard-encodings>`_

        :keyword str errors: `error handling <http://docs.python.org/library/
          codecs.html#codec-base-classes>`_ for encoding

        :rtype: :mod:`knife` :term:`object`

        >>> test = __([1], True, r't', b('i'), u('g'), None, (1,))
        >>> test.bytes().oneach().peek()
        ['[1]', 'True', 't', 'i', 'g', 'None', '(1,)']
        '''
        self._wrapper = lambda x: tobytes(x, encoding, errors)
        return self

    def unicode(self, encoding='utf_8', errors='strict'):
        '''
        :func:`unicode` (:func:`str` under Python 3) :meth:`~str.decode`
        outgoing things.

        :keyword str encoding: Unicode `encoding <http://docs.python.org/
          library/codecs.html#standard-encodings>`_

        :keyword str errors: `error handling <http://docs.python.org/library/
          codecs.html#codec-base-classes>`_ for decoding

        :rtype: :mod:`knife` :term:`object`

        >>> test = __([1], True, r't', b('i'), u('g'), None, (1,))
        >>> test.unicode().oneach().peek()
        [u'[1]', u'True', u't', u'i', u'g', u'None', u'(1,)']
        '''
        self._wrapper = lambda x: tounicode(x, encoding, errors)
        return self

    def undo(self, snapshot=0):
        '''
        Revert incoming things to a previous snapshot.

        .. note::

          A snapshot of current incoming things is taken when a :mod:`knife`
          :term:`method` is called but before the main body of the method
          executes.

        :keyword int snapshot: number of steps ago ``1``, ``2``, ``3``, etc.

        :rtype: :mod:`knife` :term:`object`

        >>> undone = __(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
        >>> undone.peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        >>> # undo back one step
        >>> undone.append(1).undo().peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        >>> # undo back one step
        >>> undone.append(1).append(2).undo().peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3, 1]
        >>> # undo back 2 steps
        >>> undone.append(1).append(2).undo(2).peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3, 1]
        '''
        return self._undo(snapshot)

    def snapshot(self):
        '''
        Take a baseline snapshot of current incoming things.

        :rtype: :mod:`knife` :term:`object`
        '''
        return self._snapshot()

    def baseline(self):
        '''
        Restore incoming things back to the baseline :meth:`snapshot`.

        :rtype: :mod:`knife` :term:`object`

        >>> from knife import __
        >>> undone = __(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
        >>> undone.peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        >>> undone.snapshot().append(1).append(2).peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3, 1, 2]
        >>> undone.baseline().peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        '''
        return self._rollback()

    def original(self):
        '''
        Restore incoming things back to the original snapshot.

        .. note::

          THe original snapshot of incoming things is taken following the first
          :mod:`knife` :term:`method` call but before the second :mod:`knife`
          :term:`method` call (if there is a second :term:`method` call)

        :rtype: :mod:`knife` :term:`object`

        >>> undone = __(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
        >>> undone.peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        >>> undone.original().peek()
        [1, 2, 3]
        '''
        return self._revert()

    def clear(self):
        '''
        Clear everything.

        :rtype: :mod:`knife` :term:`object`
        '''
        return self._clear()
