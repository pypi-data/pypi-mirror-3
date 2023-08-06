#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module implements an alternative to Abstract Base Class provided
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
    return hasattr(obj, '__contains__')


def _is_iterable(obj):
    return hasattr(obj, '__iter__') or isinstance(obj, str)


def _is_sequence(obj):
    attrs = [
        '__len__', '__iter__', '__contains__', '__getitem__',
        '__reversed__', 'index', 'count'
    ]
    if isinstance(obj, (tuple, str)):
        return True
    return all(hasattr(obj, x) for x in attrs)


def _is_mapping(obj):
    attrs = [
        '__len__', '__iter__', '__contains__', '__getitem__', '__eq__',
        '__ne__', 'keys', 'items', 'values', 'get'
    ]
    return all(hasattr(obj, x) for x in attrs)
