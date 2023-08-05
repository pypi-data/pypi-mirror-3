node.parts.Alias
----------------
::
    >>> from plumber import plumber

A dictionary that uses the alias plumbing but does not assign an aliaser.
Therefore, no aliasing is happening.::

    >>> from node.parts import Alias
    >>> class AliasDict(dict):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (Alias,)

    >>> ad = AliasDict()
    >>> ad['foo'] = 1
    >>> ad['foo']
    1
    >>> [x for x in ad]
    ['foo']
    >>> del ad['foo']
    >>> [x for x in ad]
    []

Now the same but with a prefix aliaser.::

    >>> from node.aliasing import PrefixAliaser
    >>> aliaser = PrefixAliaser(prefix="pre-")
    >>> ad = AliasDict(aliaser=aliaser)
    >>> ad['pre-foo'] = 1
    >>> ad['pre-foo']
    1
    >>> [x for x in ad]
    ['pre-foo']
    >>> del ad['pre-foo']
    >>> [x for x in ad]
    []

KeyErrors in the backend are caught and reraised with the value of the aliased
key.::

    >>> class FakeDict(object):
    ...     def __delitem__(self, key):
    ...         raise KeyError(key)
    ...     def __getitem__(self, key):
    ...         raise KeyError(key)
    ...     def __iter__(self):
    ...         yield 'foo'
    ...     def __setitem__(self, key, val):
    ...         raise KeyError(key)

    >>> class FailDict(FakeDict):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (Alias,)

    >>> fail = FailDict(aliaser=aliaser)
    >>> fail['pre-foo'] = 1
    Traceback (most recent call last):
    ...
    KeyError: 'pre-foo'

    >>> fail['pre-foo']
    Traceback (most recent call last):
    ...
    KeyError: 'pre-foo'

    >>> del fail['pre-foo']
    Traceback (most recent call last):
    ...
    KeyError: 'pre-foo'

A prefix aliaser cannot raise a KeyError, nevertheless, if it does, that error
must not be caught by the code that handle alias KeyErrors for whitelisting
(see below).::

    >>> def failalias(key):
    ...     raise KeyError
    >>> fail.aliaser.alias = failalias
    >>> [x for x in fail]
    Traceback (most recent call last):
    ...
    KeyError

    >>> from node.aliasing import DictAliaser
    >>> dictaliaser = DictAliaser(data=(('foo', 'f00'), ('bar', 'b4r')))

    >>> ad = AliasDict(aliaser=dictaliaser)
    >>> ad['foo'] = 1
    >>> [x for x in ad]
    ['foo']

Let's put a key in the dict, that is not mapped by the dictionary aliaser. This
is not possible through the plumbing ``__setitem__``, we need to use
``dict.__setitem``.::

    >>> ad['abc'] = 1
    Traceback (most recent call last):
    ...
    KeyError: 'abc'

    >>> dict.__setitem__(ad, 'abc', 1)
    >>> [x for x in ad]
    ['foo']

To see the keys that are really in the dictionary, we use ``dict.__iter__``,
not the plumbing ``__iter__``.::

    >>> [x for x in dict.__iter__(ad)]
    ['abc', 'f00']
