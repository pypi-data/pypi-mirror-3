#!/usr/bin/env python
# -*- coding: utf-8 -*-

import adm._compatibility._unittest as unittest

from adm.location import Location
from adm.location import _UNSPECIFIED


class TestLocationNormalizeArgs(unittest.TestCase):

    def test_simple_location(self):
        keys, adapter, keywords = Location._normalize_args(0)
        self.assertEqual(keys, [0])
        self.assertIs(adapter, _UNSPECIFIED)
        self.assertEqual(keywords, {})

        keys, adapter, keywords = Location._normalize_args(u'first_name')
        self.assertEqual(keys, [u'first_name'])
        self.assertEqual(keywords, {})

    def test_compound_location(self):
        keys, adapter, keywords = Location._normalize_args(0, 1)
        self.assertEqual(keys, [0, 1])
        self.assertIs(adapter, _UNSPECIFIED)
        self.assertEqual(keywords, {})

        keys, adapter, keywords = \
            Location._normalize_args(u'first_name', u'last_name')
        self.assertEqual(keys, [u'first_name', u'last_name'])
        self.assertIs(adapter, _UNSPECIFIED)
        self.assertEqual(keywords, {})

    def test_keyword_location(self):
        keys, adapter, keywords = Location._normalize_args(keys=0)
        self.assertEqual(keys, [0])
        self.assertIs(adapter, _UNSPECIFIED)
        message = u'location must be removed from kwds leaving it empty.'
        self.assertEqual(keywords, {}, message)

        keys, adapter, keywords = \
            Location._normalize_args(keys=u'first_name')
        self.assertEqual(keys, [u'first_name'])
        self.assertIs(adapter, _UNSPECIFIED)
        self.assertEqual(keywords, {})

        keys, adapter, keywords = Location._normalize_args(keys=[0, 1])
        self.assertEqual(keys, [0, 1])
        self.assertIs(adapter, _UNSPECIFIED)
        self.assertEqual(keywords, {})

        keys, adapter, keywords = \
            Location._normalize_args(keys=[0, 1], adapter=None,
                                     form=None)
        self.assertEqual(keys, [0, 1])
        self.assertIsNone(adapter)
        message = (u'location and adapter must be removed from kwds but '
                   u'other keyword arguments must remain untouched.')
        self.assertEqual(keywords, {u'form': None}, message)

    def test_adapter(self):
        # TODO: test basic adapter as keyword
        # TODO: test bound method as adapter
        pass

    def test_inlined_adapter(self):
        fn = lambda x: x.strip()

        keys, adapter, keywords = Location._normalize_args(0, fn)
        self.assertEqual(keys, [0])
        self.assertEqual(adapter, fn)
        self.assertEqual(keywords, {})

        subloc1 = Location(1)
        subloc2 = Location(2)
        keys, adapter, keywords = \
            Location._normalize_args(subloc1, subloc2)
        self.assertIs(adapter, _UNSPECIFIED,
                      (u'Location objects are callable but they cannot '
                       u'be used as adapters.'))
        self.assertEqual(keys, [subloc1, subloc2])
        self.assertEqual(keywords, {})

        keys, adapter, keywords = Location._normalize_args([1, 2], fn)
        self.assertEqual(keys, [1, 2])
        self.assertEqual(adapter, fn)
        self.assertEqual(keywords, {})

        keys, adapter, keywords = Location._normalize_args(fn)
        message = (u'A single argument must be treated as a location '
                   u'whether it is callable or not.')
        self.assertIs(adapter, _UNSPECIFIED, message)
        self.assertEqual(keys, [fn], message)

        keys, adapter, keywords = Location._normalize_args(keys=[0, fn])
        message = (u'Although fn is unlikely to be a valid location, it '
                   u'must not be treated as an inlined adapter when '
                   u'either parameter (location or adapter) is defined '
                   u'explicitly.')
        self.assertEqual(keys, [0, fn], message)
        self.assertIs(adapter, _UNSPECIFIED, message)
        self.assertEqual(keywords, {}, message)

        keys, adapter, keywords = \
            Location._normalize_args(0, fn, adapter=None)
        self.assertEqual(keys, [0, fn], message)
        self.assertIsNone(adapter, message)
        self.assertEqual(keywords, {}, message)


class TestLocationValidatePair(unittest.TestCase):
    def test_simple_validation(self):
        u"""A variety of valid key/adapter pairs -- these statements
        should not raise Exceptions.

        """
        # One key & no adapter.
        Location._validate_pair([0],     None)
        Location._validate_pair([-1],    None)
        Location._validate_pair([u'foo'], None)

        # One key & adapter using exactly one argument.
        Location._validate_pair([0], lambda x: x.strip())

        # Two keys & adapter using exactly two arguments.
        Location._validate_pair([0, 1], lambda x,y: x+u' '+y)

        # Multiple keys & no adapter.
        Location._validate_pair([u'foo', u'bar', u'baz'], None)

        # Varying keys & adapter using one or more arguments.
        Location._validate_pair([0],    lambda *x: u''.join(x))
        Location._validate_pair([0, 1], lambda *x: u''.join(x))

        # Varying keys & adapter using two or less arguments.
        Location._validate_pair([0],    lambda x, y=u'': x + y)
        Location._validate_pair([0, 1], lambda x, y=u'': x + y)

    def test_invalid_location(self):
        def unhashable1():
            keys = ([], [])
            Location._validate_pair(keys, adapter=None)
        pattern = u"keys contains unhashable type 'list'"
        self.assertRaisesRegex(TypeError, pattern, unhashable1)

        def unhashable2():
            class _UnhashableFoo(object):
                __hash__ = None
            keys = (_UnhashableFoo(),)
            Location._validate_pair(keys, adapter=None)
        pattern = u"keys contains unhashable type '_UnhashableFoo'"
        self.assertRaisesRegex(TypeError, pattern, unhashable2)

        def nonsequence():  # Must be ordered (sequence).
            keys = set([0, 1])
            Location._validate_pair(keys, adapter=None)
        pattern = u"keys is non-sequence type 'set'"
        self.assertRaisesRegex(TypeError, pattern, nonsequence)

    def test_invalid_adapter(self):
        def uncallable():
            Location._validate_pair([0], adapter=u'uncallable string')
        pattern = u"adapter is uncallable type '(str|unicode)'"
        self.assertRaisesRegex(TypeError, pattern, uncallable)

        def useskeywords():
            fn = lambda **kwds: kwds.values()
            Location._validate_pair([0], adapter=fn)
        pattern = u'adapter must not use keyword arguments'
        self.assertRaisesRegex(AttributeError, pattern, useskeywords)

    def test_mismatched_pair(self):
        def exactly1gives2():
            adapter = lambda x: x.strip()
            Location._validate_pair((0, 1), adapter)
        pattern = (u"adapter '<lambda>' takes exactly 1 argument "
                   u"\(keys gives 2\)")
        self.assertRaisesRegex(AttributeError, pattern, exactly1gives2)

        def atleast3gives2():
            adapter = lambda x,y,*z: x+y+u' '.join(z)  # Uses variable args.
            Location._validate_pair((0, 1), adapter)
        pattern = (u"adapter '<lambda>' takes at least 3 arguments "
                   u"\(keys gives 2\)")
        self.assertRaisesRegex(AttributeError, pattern, atleast3gives2)

        def atmost2gives3():
            adapter = lambda x,y=u'0000': x+u'-'+y  # Uses a default.
            Location._validate_pair((0, 1, 2), adapter)
        pattern = (u"adapter '<lambda>' takes at most 2 arguments "
                   u"\(keys gives 3\)")
        self.assertRaisesRegex(AttributeError, pattern, atmost2gives3)


class TestLocationUpdate(unittest.TestCase):
    def setUp(self):
        class LocationNoInit(Location):  # Subclass Location and
            def __init__(self):          # knock-out __init__ method to
                self._adapter = None     # prevent side effects from
                self._keys = ()          # instantiation.
        self.myloc = LocationNoInit()

    def test_full_update_and_getters(self):
        loc = Location(1)  # update method is called via __init__.
        self.assertEqual(loc.keys, (1,))
        self.assertIsNone(loc.adapter)

        fn = lambda x: x.strip()
        loc = Location(1, fn)
        self.assertEqual(loc.keys, (1,))
        self.assertEqual(loc.adapter, fn)

    def test_partial_update(self):
        fn = lambda x: x.strip()
        self.myloc.update(1, fn)
        self.assertEqual(self.myloc.keys, (1,))
        self.assertEqual(self.myloc.adapter, fn)

        self.myloc.update(0)  # Update location from previous check.
        self.assertEqual(self.myloc.keys, (0,))
        message = (u'Only updating location, adapter should remain '
                   u'unchanged.')
        self.assertEqual(self.myloc.adapter, fn, message)

        self.myloc.update(1, 2, lambda x,y: x+u'-'+y)  # Reset location & adapter.
        self.myloc.update(adapter=None)  # Update adapter only.
        self.assertEqual(self.myloc.adapter, None)
        message = (u'Only updating adapter, location should remain '
                   u'unchanged.')
        self.assertEqual(self.myloc.keys, (1, 2), message)

    def test_updates_and_getters(self):
        self.myloc.update(1)
        self.assertEqual(self.myloc.keys, (1,))
        self.assertIsNone(self.myloc.adapter)

        fn = lambda x,y: x+u'-'+y
        self.myloc.update(1, 2, fn)
        self.assertEqual(self.myloc.keys, (1, 2))
        self.assertEqual(self.myloc.adapter, fn)


#python -m unittest adm.tests.location2_test.TestLocationCall
class TestLocationCall(unittest.TestCase):
    def setUp(self):
        self.samplelst = [u'Mary', u'Smith', u'1382']
        self.sampledic = {u'FirstName':u'Mary', u'LastName': u'Smith',
                          u'IdNumber': u'1382'}
        # ??? MAYBE: Automatic handling for property mapping.
        # self.sampleobj = SomeClass('Mary', 'Smith', '1382')

    def test_single_key(self):
        loc = Location(0)
        result = loc(self.samplelst)
        self.assertEqual(result, u'Mary')

        loc = Location(u'FirstName')
        result = loc(self.sampledic)
        self.assertEqual(result, u'Mary')

    def test_multiple_keys_with_adapter(self):
        loc = Location(u'FirstName', u'LastName', lambda x,y: x + u' ' + y)
        result = loc(self.sampledic)
        self.assertEqual(result, u'Mary Smith')

    def test_multiple_keys_no_adapter(self):
        loc = Location(0, 1)
        result = loc(self.samplelst)
        self.assertEqual(result, {0: u'Mary', 1: u'Smith'})

        loc = Location(u'FirstName', u'LastName')
        result = loc(self.sampledic)
        self.assertEqual(result, {u'FirstName': u'Mary',
                                  u'LastName': u'Smith'})


if __name__ == u'__main__':
    unittest.main()

