#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""This module implements an alternative to Abstract Base Class provided
interface-assertion to help support Python versions 2.5 and earlier.

There are instances in adm's current implementation where EAFP style
type-handling can result in confusing and misleading error messages. To
manage these cases, this code occasionally uses LBYL idioms that are
best implemented with Abstract Base Classes (new in Python 2.6).

Unfortunately, ABCs are not easily handled using the compatibility
layer. To provide support for older versions of Python, the following
interface-checking functions should be used.

"""

from adm._compatibility._builtins import *


def _is_hashable(obj):
    try:
        val = hash(obj)
    except TypeError:
        val = None
    return val is not None


def _is_container(obj):
    return hasattr(obj, u'__contains__')


def _is_iterable(obj):
    return hasattr(obj, u'__iter__') or isinstance(obj, unicode)


def _is_sequence(obj):
    attrs = [
        u'__len__', u'__iter__', u'__contains__', u'__getitem__',
        u'__reversed__', u'index', u'count'
    ]
    if isinstance(obj, (tuple, unicode)):
        return True
    return all(hasattr(obj, x) for x in attrs)


def _is_mapping(obj):
    attrs = [
        u'__len__', u'__iter__', u'__contains__', u'__getitem__', u'__eq__',
        u'__ne__', u'keys', u'items', u'values', u'get'
    ]
    return all(hasattr(obj, x) for x in attrs)
