#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
"""
#from __future__ import absolute_import  # Only available in Python 2.5
                                         # and later.

from sys import version_info as __python_version

if __python_version[:2] >= (2, 7):
    import adm._compatibility._pprint as pprint  # Must first import
                                                 # pprint in case it
                                                 # needs to be patched.
    from unittest import *

else:
    from unittest2 import *


try:
    TestCase.assertRaisesRegex
except AttributeError:
    # Method name changed in Python 3.2
    TestCase.assertRaisesRegex = TestCase.assertRaisesRegexp

