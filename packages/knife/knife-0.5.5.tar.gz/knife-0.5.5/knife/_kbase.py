# -*- coding: utf-8 -*-
'''base knife keys'''

from appspace.keys import AppspaceKey


class KChainknife(AppspaceKey):

    '''base knife key'''

    def __init__(*things, **kw):  # @NoSelf
        '''
        Initialize :mod:`knife`.

        :argument things: incoming things
        :keyword integer snapshots: snapshots to keep (default: ``5``)
        '''

    def apply(worker, *args, **kw):  # @NoSelf
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

    def worker(worker):  # @NoSelf
        '''
        Assign :func:`callable` used to work on incoming things.

        .. note::

          Global :term:`positional argument`\s and :term:`keyword argument`\s
          assigned with :meth:`params` are reset whenever a new `worker` is
          assigned.

        :argument worker: a :func:`callable`

        :rtype: :mod:`knife` :term:`object`
        '''

    def params(*args, **kw):  # @NoSelf
        '''
        Assign :term:`positional argument`\s and :term:`keyword argument`\s
        to be used globally.

        :rtype: :mod:`knife` :term:`object`
        '''

    def pattern(pattern, type='parse', flags=0):  # @NoSelf
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

    def prepend(*things):  # @NoSelf
        '''
        Insert `things` **before** other incoming things.

        :argument things: incoming things

        :rtype: :mod:`knife` :term:`object`

        >>> __(3, 4, 5).prepend(1, 2, 3, 4, 5, 6).peek()
        [1, 2, 3, 4, 5, 6, 3, 4, 5]
        '''

    def append(*things):  # @NoSelf
        '''
        Insert `things` **after** other incoming things.

        :argument things: incoming things

        :rtype: :mod:`knife` :term:`object`

        >>> from knife import __
        >>> __(3, 4, 5).append(1, 2, 3, 4, 5, 6).peek()
        [3, 4, 5, 1, 2, 3, 4, 5, 6]
        '''

    def pipe(self, knife):
        '''
        Pipe incoming things from some other :mod:`knife` :term:`object`
        through this :mod:`knife` :term:`object`.

        :argument knife: another :mod:`knife` :term:`object`

        :rtype: :mod:`knife` :term:`object`
        '''

    def back(self):
        '''
        Switch back to :mod:`knife` :term:`object` that piped its incoming
        things through this :mod:`knife` :term:`object`.

        :rtype: :mod:`knife` :term:`object`
        '''

    def __len__():  # @NoSelf
        '''Number of incoming things.'''

    def __repr__():  # @NoSelf
        '''String representation.'''


class KOutput(KChainknife):

    '''output key'''

    def __iter__():  # @NoSelf
        '''Iterate over outgoing things.'''

    def get():  # @NoSelf
        '''
        Return outgoing things wrapped with :meth:`wrap`.

        .. note::

          With only one outgoing thing, only that one outgoing thing is
          returned. With multiple outgoing things, they are returned wrapped
          with the wrapper assigned with :meth:`wrap` (default wrapper is
          :func:`list`).
        '''

    def peek():  # @NoSelf
        '''
        Preview current incoming things wrapped with :meth:`wrap`.

        .. note::

          With only one outgoing thing, only that one thing is returned. With
          multiple outgoing things, everything is returned wrapped with the
          wrapper assigned with :meth:`wrap` (default wrapper is :func:`list`).
        '''

    def wrap(wrapper):  # @NoSelf
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

    def oneach():  # @NoSelf
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

    def ascii(errors='strict'):  # @NoSelf
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

    def bytes(encoding='utf-8', errors='strict'):  # @NoSelf
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

    def unicode(encoding='utf-8', errors='strict'):  # @NoSelf
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

    def undo(snapshot=0):  # @NoSelf
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

    def snapshot():  # @NoSelf
        '''
        Take a baseline snapshot of current incoming things.

        :rtype: :mod:`knife` :term:`object`
        '''

    def baseline():  # @NoSelf
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

    def original():  # @NoSelf
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

    def clear():  # @NoSelf
        '''
        Clear everything.

        :rtype: :mod:`knife` :term:`object`
        '''
