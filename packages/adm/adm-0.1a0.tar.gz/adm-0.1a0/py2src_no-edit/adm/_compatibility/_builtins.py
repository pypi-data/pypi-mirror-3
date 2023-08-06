#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""

"""

try:
    all  # New in 2.5
except NameError:
    def all(iterable):
        for element in iterable:
            if not element:
                return False
        return True

try:
    any  # New in 2.5
except NameError:
    def any(iterable):
        for element in iterable:
            if element:
                return True
        return False

try:
    next  # New in 2.6
except NameError:
    def next(iterator):
        return iterator.next()

try:
    map.__iter__  # Added as part of Python 3 implementation.
except AttributeError:
    from adm._compatibility._itertools import imap as map


try:
    property.setter  # New in 2.6
except AttributeError:
    # Code taken from cpython/Doc/howto/descriptor.rst source file.
    # The setter and deleter methods were added as well as other small
    # changes for 3to2 compatibility.
    class property(object):

        def __init__(self, fget=None, fset=None, fdel=None, doc=None):
            self.fget = fget
            self.fset = fset
            self.fdel = fdel
            self.__doc__ = doc

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            if self.fget is None:
                raise AttributeError(u"unreadable attribute")
            return self.fget(obj)

        def __set__(self, obj, value):
            if self.fset is None:
                raise AttributeError(u"can't set attribute")
            self.fset(obj, value)

        def __delete__(self, obj):
            if self.fdel is None:
                raise AttributeError(u"can't delete attribute")
            self.fdel(obj)

        def setter(self, func):
            self.fset = func
            return self

        def deleter(self, func):
            self.fdel = func
            return self
