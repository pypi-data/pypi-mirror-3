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

    def worker(worker):  # @NoSelf
        '''
        Assign `callable <http://docs.python.org/library/functions.html#
        callable>`_ used to work on incoming things.

        Global `positional <http://docs.python.org/glossary.html#term-
        positional-argument>`_ and `keyword <http://docs.python.org/glossary.
        html#term-keyword-argument>`_ :meth:`params` are reset when a new
        `worker` is assigned.

        :argument worker: a callable

        :rtype: :const:`self` (:obj:`knife` object)
        '''

    def params(*args, **kw):  # @NoSelf
        '''
        Assign `positional <http://docs.python.org/glossary.html#term-
        positional-argument>`_ and `keyword <http://docs.python.org/glossary.
        html#term-keyword-argument>`_ arguments used when :meth:`worker` is
        invoked.

        :rtype: :const:`self` (:obj:`knife` object)
        '''

    def pattern(pattern, type='parse', flags=0):  # @NoSelf
        '''
        Compile search `pattern` for use as :meth:`worker`.

        Global `positional <http://docs.python.org/glossary.html#term-
        positional-argument>`_ and `keyword <http://docs.python.org/glossary.
        html#term-keyword-argument>`_:meth:`params` are reset when a pattern
        is compiled.

        :argument string pattern: search pattern

        :keyword string type: engine to compile `pattern` with. Valid options
          are `'parse' <http://pypi.python.org/pypi/parse/>`_, `'re'
          <http://docs.python.org/library/re.html>`_, or `'glob' <http://docs.
          python.org/library/fnmatch.html>`_

        :keyword integer flags: regular expression `flags
          <http://docs.python.org/library/re.html#re.DEBUG>`_

        :rtype: :const:`self` (:obj:`knife` object)

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

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(3, 4, 5).prepend(1, 2, 3, 4, 5, 6).peek()
        [1, 2, 3, 4, 5, 6, 3, 4, 5]
        '''

    def append(*things):  # @NoSelf
        '''
        Insert `things` **after** other incoming things.

        :argument things: incoming things

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from knife import __
        >>> __(3, 4, 5).append(1, 2, 3, 4, 5, 6).peek()
        [3, 4, 5, 1, 2, 3, 4, 5, 6]
        '''

    def pipe(self, knife):
        '''
        Pipe incoming things through another :mod:`knife`.

        :argument knife: another :mod:`knife`

        :rtype: :const:`self` (:obj:`knife` object)
        '''

    def back(self):
        '''
        Switch back to the previous :mod:`knife` object that piped its incoming
        things through this :mod:`knife`.

        :rtype: :const:`self` (:obj:`knife` object)
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

        If there's only one outgoing thing, only that thing will be returned.
        If there are multiple outgoing things, they will be returned wrapped
        with :meth:`wrap`.
        '''

    def peek():  # @NoSelf
        '''
        Preview current incoming things wrapped with :meth:`wrap`.

        If there's only one outgoing thing, only that thing will be returned.
        If there are multiple outgoing things, they will be returned wrapped
        with :meth:`wrap`.
        '''

    def wrap(wrapper):  # @NoSelf
        '''
        Assign :class:`object`, :class:`type`, or :obj:`class` used to wrap
        outgoing things.

        Default wrapper is :class:`list`. The default wrapper is reverted to
        after :meth:`get` or :meth:`peek` is invoked.

        :argument wrapper: an :class:`object`, :class:`type`, or :obj:`class`

        :rtype: :const:`self` (:obj:`knife` object)

        >>> __(1, 2, 3, 4, 5, 6).wrap(tuple).peek()
        (1, 2, 3, 4, 5, 6)
        '''

    def oneach():  # @NoSelf
        '''
        Toggle whether each outgoing thing should be individually wrapped with
        :meth:`wrap` or whether all outgoing things should be wrapped with
        :meth:`wrap` all at once.

        Default behavior is to :meth:`wrap` everything at once. The default
        behavior is reverted to **after** :meth:`get` or :meth:`peek` is
        invoked.

        :rtype: :const:`self` (:obj:`knife` object)
        '''

    def ascii(errors='strict'):  # @NoSelf
        '''
        `byte <http://docs.python.org/py3k/library/functions.html#bytes>`_
        `encode() <http://docs.python.org/py3k/library/stdtypes.html#str.
        encode>`_ outgoing things with the ``'ascii'`` codec.

        :keyword string errors: error handling for decoding issues

        :rtype: :const:`self` (:obj:`knife` object)

        >>> from stuf.six import u, b
        >>> test = __([1], True, r't', b('i'), u('g'), None, (1,))
        >>> test.ascii().oneach().peek()
        ['[1]', 'True', 't', 'i', 'g', 'None', '(1,)']
        '''

    def bytes(encoding='utf-8', errors='strict'):  # @NoSelf
        '''
        `byte <http://docs.python.org/py3k/library/functions.html#bytes>`_
        `encode() <http://docs.python.org/py3k/library/stdtypes.html#str.
        encode>`_ outgoing things.

        :keyword string encoding: Unicode encoding

        :keyword string errors: error handling for encoding issues

        :rtype: :const:`self` (:obj:`knife` object)

        >>> test = __([1], True, r't', b('i'), u('g'), None, (1,))
        >>> test.bytes().oneach().peek()
        ['[1]', 'True', 't', 'i', 'g', 'None', '(1,)']
        '''

    def unicode(encoding='utf-8', errors='strict'):  # @NoSelf
        '''
        `unicode <http://docs.python.org/library/functions.html#unicode>`_
        (`str <http://docs.python.org/py3k/library/functions.html#str>`_ under
        Python 3) `decode() <http://docs.python.org/py3k/library/stdtypes.html
        #bytes.decode>`_ outgoing things.

        :keyword string encoding: Unicode encoding

        :keyword string errors: error handling for decoding issues

        :rtype: :const:`self` (:obj:`knife` object)

        >>> test = __([1], True, r't', b('i'), u('g'), None, (1,))
        >>> test.unicode().oneach().peek()
        [u'[1]', u'True', u't', u'i', u'g', u'None', u'(1,)']
        '''

    def undo(snapshot=0):  # @NoSelf
        '''
        Restore incoming things to a previous snapshot.

        A snapshot of incoming things is automatically taken at the start of
        each :mod:`knife` operation.

        :keyword integer snapshot: number of steps ago ``1``, ``2``, ``3``,
          etc.

        :rtype: :const:`self` (:obj:`knife` object)

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
        Take baseline snapshot of current incoming things.

        :rtype: :const:`self` (:obj:`knife` object)
        '''

    def baseline():  # @NoSelf
        '''
        Restore incoming things to baseline :meth:`snapshot`.

        :rtype: :const:`self` (:obj:`knife` object)

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
        Restore incoming things to original snapshot.

        :rtype: :const:`self` (:obj:`knife` object)

        >>> undone = __(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
        >>> undone.peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        >>> undone.original().peek()
        [1, 2, 3]
        '''

    def clear():  # @NoSelf
        '''
        Clear everything.

        :rtype: :const:`self` (:obj:`knife` object)
        '''
