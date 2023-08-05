##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__all__ = ['mappingobject']

class mappingobject(object):
    """\
    Sometimes, you want to use a mapping object like a regular object.

    ``zc.mappingobject`` provides a wrapper for a mapping objects that
    provides both attribute and item access.

    >>> import zc.mappingobject
    >>> mapping = dict(a=1)
    >>> ob = zc.mappingobject.mappingobject(mapping)

    >>> ob.a
    1
    >>> ob.a = 2
    >>> ob.a
    2
    >>> mapping
    {'a': 2}

    >>> list(ob)
    ['a']

    >>> len(ob)
    1

    >>> ob['a'] = 3
    >>> ob.a
    3
    >>> mapping
    {'a': 3}

    >>> del ob.a
    >>> mapping
    {}
    >>> ob.a
    Traceback (most recent call last):
    ...
    AttributeError: a

    >>> ob.b = 1
    >>> mapping
    {'b': 1}

    >>> del ob['b']
    >>> mapping
    {}
    """
    __slots__ = '_mappingobject__data',

    def __init__(self, data):
        super(mappingobject, self).__setattr__('_mappingobject__data', data)

    def __getattr__(self, name):
        try:
            return self.__data[name]
        except KeyError:
            raise AttributeError(name)

    def __delattr__(self, name):
        try:
            del self.__data[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self.__data[name] = value

    def __getitem__(self, name):
        return self.__data[name]

    def __delitem__(self, name):
        del self.__data[name]

    __setitem__ = __setattr__

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)


def test_suite():
    import doctest
    return doctest.DocTestSuite()
