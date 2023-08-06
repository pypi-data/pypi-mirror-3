#!/usr/bin/env python
# -*- coding: utf-8 -*-
from inspect import *

try:
    getfullargspec  # New in Python 3.0 (getargspec was deprecated).
                    # 3to2 has a fixer for this (fullargspec) but it
                    # should be disabled.
except NameError:
    def getfullargspec(func):
        # The new getfullargspec returns three additional, Python 3
        # specific, items (kwonlyargs, kwonlydefaults, annotations).
        # We add None values so the returned tuple is the same length.
        return getargspec(func) + (None, None, None)

