#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import adm._compatibility._unittest as unittest
import re
from adm._compatibility._collections import Counter

from adm.detection import Locator
from adm.detection import total_classifier
from adm.detection import column_classifier
from adm.detection import element_classifier


class TestClassifierDecoration(unittest.TestCase):
    def _test_decoration(self, wrapped_function, original_function):
        self.assertEqual(wrapped_function.__name__ , u'wrapped',
                         msg=u"The decorated function should have the "
                             u"name 'wrapped' instead of its original "
                             u"name to prevent confusion.")

        self.assertIs(wrapped_function.__wrapped__, original_function,
                         msg=u"The function referenced by __wrapped__ "
                             u"should be the original, unwrapped "
                             u"function.")

        self.assertTrue(hasattr(wrapped_function, u'_is_classifier'),
                        msg=u'The _is_classifier attribute is needed to '
                            u'determine if a function can be used as-is '
                            u'or if it needs to be wrapped.')

        self.assertTrue(wrapped_function._is_classifier)  # Expects True

    def test_total_classifier(self):
        def total_fn(iterable):
            return {}
        wrapped_fn = total_classifier(total_fn)      # Wrap explicitly.
        self._test_decoration(wrapped_fn, total_fn)

    def test_column_classifier(self):
        def column_fn(iterable):
            return 1
        wrapped_fn = column_classifier(column_fn)    # Wrap explicitly.
        self._test_decoration(wrapped_fn, column_fn)

    def test_element_classifier(self):
        def element_fn(iterable):
            return 1
        wrapped_fn = element_classifier(element_fn)  # Wrap explicitly.
        self._test_decoration(wrapped_fn, element_fn)


class TestTotalClassifier(unittest.TestCase):
    def setUp(self):
        # Define basic "Total Classifier".
        @total_classifier
        def is_county_fips(iterable):
            results = Counter()
            total = 0
            for mapping in iterable:
                for k,v in mapping.items():
                    # If code is three digits and odd, then it matches.
                    if (len(unicode(v)) == 3 and unicode(v).isdigit() and
                        int(v) % 2 == 1):
                        results[k] += 1
                    else:
                        results[k] += 0
                total += 1
            return dict((k, v/total) for k,v in results.items())

        self.is_county_fips = is_county_fips  # Assign as static method.

    def test_total_classifier(self):
        sample = [[u'Cuyahoga',   u'035', 18],
                  [u'Franklin',   u'049', 25],
                  [u'Hamilton',   u'061', 31],
                  [u'Montgomery', u'113', 57]]
        result = self.is_county_fips(sample)
        self.assertEqual(result, {0: 0, 1: 1, 2: 0})

        sample = [{u'NAME': u'Cuyahoga',   u'CODE': u'035', u'ORD': 18},
                  {u'NAME': u'Franklin',   u'CODE': u'049', u'ORD': 25},
                  {u'NAME': u'Hamilton',   u'CODE': u'061', u'ORD': 31},
                  {u'NAME': u'Montgomery', u'CODE': u'113', u'ORD': 57}]
        result = self.is_county_fips(sample)
        self.assertEqual(result, {u'NAME': 0, u'CODE': 1, u'ORD': 0})

    def test_notiterable(self):
        def notiterable():
            result = self.is_county_fips(1000)
        pattern = u"'int' type is not iterable"
        self.assertRaisesRegex(TypeError, pattern, notiterable)

    def test_baditerator(self):
        def baditerator():
            result = self.is_county_fips(u'bad iterator')
        pattern = (u"instead, received a string \(an iterable "
                   u"collection of characters\) -- this is not allowed.")
        self.assertRaisesRegex(TypeError, pattern, baditerator)

    def test_badsequence(self):
        def badsequence1():
            badsample = [0, 1, 2, 3, 4]
            result = self.is_county_fips(badsample)
        pattern = u"non-sequence or string type 'int'"
        self.assertRaisesRegex(TypeError, pattern, badsequence1)

        def badsequence2():
            badsample = [u'Cuyahoga', u'Franklin', u'Hamilton']
            result = self.is_county_fips(badsample)
        pattern = (u"received a collection containing strings -- this "
                   u"is not allowed.")
        pattern = u"non-sequence or string type '(str|unicode)'"
        self.assertRaisesRegex(TypeError, pattern, badsequence2)

    def test_badresults(self):
        def badvalue():
            @total_classifier
            def dummyclassifier(sample):
                return {0: 0, 1: 1.2}  # Value 1.2 is illegal.
            dummyclassifier([[], [], []])  # Using dummy sample.
        pattern = u'contains illegal values'
        self.assertRaisesRegex(ValueError, pattern, badvalue)

        def badtype():
            @total_classifier
            def dummyclassifier(sample):
                return {0: 0, 1: u'foo'}  # Type 'str' is illegal.
            dummyclassifier([[], [], []])  # Using dummy sample.
        pattern = u"contains illegal type '(?:str|unicode)'"
        self.assertRaisesRegex(TypeError, pattern, badtype)


class TestColumnClassifier(unittest.TestCase):
    def test_classifier(self):
        @column_classifier
        def cheapbenfords(iterator):
            u"""Compare frequency of ones in the leading digit position
            to frequency of ones expected by Benford's Law.  A more
            comprehensive Benford's check would perform frequency
            correlation for all digits -- but this is quick-and-cheap
            for testing.

            """
            starts_with_one = 0
            sample_size = 0
            for num in iterator:
                if unicode(num).startswith(u'1'):
                    starts_with_one += 1
                sample_size += 1
            freq_of_ones = starts_with_one / sample_size
            expected_freq = 0.30103  # Freq of ones in Benford's Law.
            values = [freq_of_ones, expected_freq]
            return min(values) / max(values)

        sample = [[0, 1,      0],  # Index 1 contains factorials.
                  [0, 1,      0],
                  [0, 2,      0],
                  [0, 6,      0],
                  [0, 24,     0],
                  [0, 120,    0],
                  [0, 720,    0],
                  [0, 5040,   0],
                  [0, 40320,  0],
                  [0, 362880, 0]]
        result = cheapbenfords(sample)
        self.assertEqual(set(result.keys()), set([0, 1, 2]))
        self.assertEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], 0.997, places=3)
        self.assertEqual(result[2], 0.0)


class TestElementClassifier(unittest.TestCase):
    def test_binary_classifier(self):
        @element_classifier
        def is_odd(x):  # Binary classifier returns only True or False.
            return x % 2 == 1

        sample = [[0, 1, 1],
                  [0, 1, 1],
                  [0, 1, 1],
                  [0, 0, 1],
                  [0, 0, 1],
                  [0, 0, 1],
                  [0, 0, 1],
                  [0, 0, 1],
                  [0, 0, 0],
                  [0, 0, 0]]
        results = is_odd(sample)
        self.assertEqual(results, {0: 0.0, 1: 0.3, 2: 0.8})

    def test_ternary_classifier(self):
        @element_classifier
        def is_letter_grade(item):
            if not item:  # Return None for empty items.
                return None
            return unicode(item).upper() in [u'A', u'B', u'C', u'D', u'F']

        sample = [[u'', u'A',   u''],
                  [u'', u'B',   u''],
                  [u'', u'C',   u''],
                  [u'', u'D',   u''],
                  [u'', u'foo', u''],
                  [u'', u'',    u''],
                  [u'', u'',    u''],
                  [u'', u'',    u''],
                  [u'', u'',    u''],
                  [u'', u'',    u'']]
        results = is_letter_grade(sample)
        self.assertEqual(results, {0: 0, 1: 0.8, 2: 0},
                         msg=u'The five empty items are not classified. '
                             u'Four of the remaining five items are '
                             u'classified as letter grades (80%).')

    def test_probabilistic_classifier(self):
        # The term 'probabilistic classifier' refers to an element
        # classifier that returns a value from zero to one instead of
        # simply True or False (or None).
        @element_classifier
        def barometer_result(item):
            avg = 1013.25  # Average pressure at sea-level in millibars.
            return min(item, avg) / max(item, avg)

        sample = [[0, 1008.08, 0],
                  [0, 1014.98, 0],
                  [0, 1018.61, 0],
                  [0, 1015.44, 0],
                  [0, 1015.02, 0],
                  [0, 1012.61, 0],
                  [0, 1008.12, 0],
                  [0, 1011.43, 0]]
        results = barometer_result(sample)
        self.assertEqual(results[0], 0.0)
        self.assertAlmostEqual(results[1], 0.9971, places=4)
        self.assertEqual(results[2], 0.0)


class TestLocatorInit(unittest.TestCase):
    def test_unwrapped_classifier(self):
        def is_phone(x):
            return bool(re.search(ur'^\d{3}-\d{3}-\d{4}$', x))
        locate_phone = Locator(foo=is_phone)

        # Get reference to classifier (foo), test that it has been
        # wrapped as an element classifier.
        foo_classifier = locate_phone.classifier[u'foo']
        self.assertTrue(foo_classifier._is_classifier,
                        u'Unwrapped functions are assumed to be element '
                        u'classifiers and are handled accordingly.')
        self.assertEqual(foo_classifier.__wrapped__, is_phone)

    def test_wrapped_classifier(self):
        @element_classifier
        def is_phone(x):
            return bool(re.search(ur'^\d{3}-\d{3}-\d{4}$', x))

        locate_phone = Locator(foo=is_phone)
        self.assertEqual(locate_phone.classifier, {u'foo': is_phone})

        locate_phone = Locator(form=is_phone)
        self.assertEqual(locate_phone.classifier, {u'form': is_phone})

    def test_adapters(self):
        def is_dummy(x):  # Dummy classifier.
            return True

        locate = Locator(dummy=is_dummy)
        self.assertEqual(locate.adapters, [None])

        def lstrip(x):              # Adapter: left-strip value.
            return unicode(x).lstrip()

        def rstrip(x):              # Adapter: right-strip value.
            return unicode(x).rstrip()

        locate = Locator(lstrip, rstrip, dummy=is_dummy)
        self.assertEqual(locate.adapters, [lstrip, rstrip])

    def test_form_handler(self):
        u"""String & regex objects should be wrapped in functions."""
        # Test with compiled object.
        regex = re.compile(ur'^\d{3}-\d{3}-\d{4}$')
        locate_phone = Locator(form=regex)

        # Test with uncompiled string.
        locate_phone = Locator(form=ur'^\d{3}-\d{3}-\d{4}$')

        # Test with container of mixed objects.
        patterns = [ur'^\(\d{3}\) \d{3}-\d{4}$',
                    re.compile(ur'^\d{3}-\d{3}-\d{4}$')]
        locate_phone = Locator(form=patterns)

    def test_freq_handler(self):
        # Pearson r correlation of value frequencies (Accept dict).
        # TODO: add key function to convert continuous values

        #benfords_pmf = {1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097,
        #                5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051,
        #                9: 0.046}
        pmf = {u'foo': 0.6, u'bar': 0.24, u'baz': 0.16}
        classify_by_freq = Locator.freq_handler(pmf)

        sample = [[0, u'foo', 0],
                  [0, u'foo', 0],
                  [0, u'foo', 0],
                  [0, u'foo', 0],
                  [0, u'foo', 0],
                  [0, u'foo', 0],
                  [0, u'qux', 0],
                  [0, u'qux', 0],
                  [0, u'bar', 0],
                  [0, u'bar', 0]]

        sample = [[0, u'foo', 0],
                  [0, u'foo', 0],
                  [0, u'foo', 0],
                  [0, u'qux', 0],
                  [0, u'bar', 0]]

        freq = classify_by_freq(sample)
        print freq
        #pass

    def test_handler_exceptions(self):
        # Test exceptions for missing handler
        pass

    def test_card_handler(self):
        # Cardnality of aggregate sample (accept integer).
        pass

    def test_head_handler(self):  # !!! TODO: Only applicable to Column not Cell.
        # Matching of header row (accept str or compiled regex or mixed collection).
        pass

    def test_entropy_handler(self):
        # Shannon Entropy of value (accept float from 0 to 1).
        # Individual or aggregate?
        pass

    def test_rel_handler(self):
        # Individual relation to other value (Functions only?  No handler?).
        pass

    def test_bayes_handler(self):
        # Bayesian classifier (What to accept?).
        pass


class TestLocatorScan(unittest.TestCase):
    #def setUp(self):
    #    self.sample = [
    #        ['3/08/12 6:37PM',  'San Jose W, CA', '408-443-3333', '2'],
    #        ['3/09/12 6:03PM',  'Greenfield, MA', '413-647-2028', '1'],
    #        ['3/09/12 7:13PM',  'Incoming',       '317-746-2235', '54'],
    #        ['3/09/12 9:57PM',  'Vm Retrieval',   '789',          '2'],
    #        ['3/09/12 10:00PM', 'La Porte, IN',   '219-282-4981', '14'],
    #        ['3/10/12 11:42AM', 'Vm Retrieval',   '789',          '1'],
    #        ['3/10/12 5:19PM',  'Washington, DC', '202-465-0711', '20'],
    #        ['3/11/12 7:09PM',  'Incoming',       '219-282-4981', '29'],
    #        ['3/11/12 7:55PM',  'Incoming',       '413-647-2028', '8'],
    #        ['3/12/12 11:13AM', 'Silver Spg, MD', '301-639-2028', '1']
    #    ]

    def test_single_classifier(self):
        sample = [[u'', u'408-443-3333', u'', u'', u'', u''],
                  [u'', u'317-746-2235', u'', u'', u'', u''],
                  [u'', u'3/09/12',      u'', u'', u'', u''],
                  [u'', u'219-282-4981', u'', u'', u'', u''],
                  [u'', u'301-639-2028', u'', u'', u'', u'']]

        locate_phone = Locator(form=ur'^\d{3}-\d{3}-\d{4}$')
        locate_phone.scan(sample, form=0.75)

        self.assertEqual(locate_phone.threshold, {u'form': 0.75})
        self.assertEqual(locate_phone.result,       # Result of scan
                         set([(0, None, u'form', 0.0),   # is a set of
                          (1, None, u'form', 0.8),   # tuples:
                          (2, None, u'form', 0.0),   #   0=objref
                          (3, None, u'form', 0.0),   #   1=adapter
                          (4, None, u'form', 0.0),   #   2=clsname
                          (5, None, u'form', 0.0)]))  #   3=clsvalue

    def test_multiple_classifiers(self):
        sample = [[u'', u'M', u''],
                  [u'', u'F', u''],
                  [u'', u'F', u''],
                  [u'', u'M', u''],
                  [u'', u'X', u'']]

        locate = Locator(foo=lambda x: x in (u'M', u'F'),
                         bar=lambda x: len(x) == 1)
        locate.scan(sample, foo=0.75, bar=0.75)

        self.assertEqual(locate.threshold, {u'foo': 0.75, u'bar': 0.75})
        self.assertEqual(locate.result,
                         set([(0, None, u'foo', 0.0),
                          (1, None, u'foo', 0.8),
                          (2, None, u'foo', 0.0),
                          (0, None, u'bar', 0.0),
                          (1, None, u'bar', 1.0),
                          (2, None, u'bar', 0.0)]))

    def test_single_adapter(self):
        sample = [[u'', u'F',     u''],
                  [u'', u'M',     u''],
                  [u'', u'f',     u''],
                  [u'', u'm    ', u''],
                  [u'', u'x    ', u'']]

        def normalize(x):
            return unicode(x).upper().strip()

        locate = Locator(normalize,  # Single, non-default, adapter.
                         foo=lambda x: x in (u'M', u'F'),
                         bar=lambda x: len(x) == 1)
        locate.scan(sample, foo=0.75, bar=0.75)

        self.assertEqual(locate.threshold, {u'foo': 0.75, u'bar': 0.75})
        self.assertEqual(locate.result,
                         set([(0, normalize, u'foo', 0.0),
                          (1, normalize, u'foo', 0.8),
                          (2, normalize, u'foo', 0.0),
                          (0, normalize, u'bar', 0.0),
                          (1, normalize, u'bar', 1.0),
                          (2, normalize, u'bar', 0.0)]))

    def test_multiple_adapters(self):
        sample = [[u'', u'F',     u''],
                  [u'', u'M',     u''],
                  [u'', u'f',     u''],
                  [u'', u'm    ', u''],
                  [u'', u'x    ', u'']]

        def normalize(x):
            return unicode(x).upper().strip()

        locate = Locator(None, normalize,  # Two adapters.
                         foo=lambda x: x in (u'M', u'F'),
                         bar=lambda x: len(x) == 1)
        locate.scan(sample, foo=0.75, bar=0.75)

        self.assertEqual(locate.threshold, {u'foo': 0.75, u'bar': 0.75})
        self.assertEqual(locate.result,
                         set([(0, None,      u'foo', 0.0),
                          (0, None,      u'bar', 0.0),
                          (1, None,      u'foo', 0.4),
                          (1, None,      u'bar', 0.6),
                          (2, None,      u'foo', 0.0),
                          (2, None,      u'bar', 0.0),
                          (0, normalize, u'foo', 0.0),
                          (0, normalize, u'bar', 0.0),
                          (1, normalize, u'foo', 0.8),
                          (1, normalize, u'bar', 1.0),
                          (2, normalize, u'foo', 0.0),
                          (2, normalize, u'bar', 0.0)]))


class TestLocatorResultMethods(unittest.TestCase):
    def test_filter_cutoff(self):           # Result of scan
        results = set([(0, None, u'foo', 0.0),   # is a set of
                   (1, None, u'foo', 0.80),  # tuples:
                   (2, None, u'foo', 0.75),  #   0=objkey
                   (3, None, u'foo', 0.70),  #   1=adapter
                   (4, None, u'foo', 0.0),   #   2=clsname
                   (5, None, u'foo', 0.0)])   #   3=clsresult
        threshold = {u'foo': 0.75}
        filtered = Locator._filter_cutoff(threshold, results)
        self.assertEqual(filtered, set([(1, None, u'foo', 0.80),
                                    (2, None, u'foo', 0.75)]))

        # Mismatched clsname keys in results and cutoff are ignored --
        # operates on subset of existing keys.
        results = set([(0, None, u'foo', 0.8),  # No 'foo' in cutoff.
                   (1, None, u'bar', 0.8)])
        cutoff = {u'bar': 0.75, u'baz': 0.80}  # No 'baz' in results.
        filtered = Locator._filter_cutoff(cutoff, results)
        self.assertEqual(filtered, set([(1, None, u'bar', 0.8)]))

    def test_filter_required(self):
        results = set([(0, None, u'foo', 0.75),
                   (1, None, u'foo', 0.80),
                   (1, None, u'bar', 0.80),
                   (2, None, u'bar', 0.75)])

        threshold = {u'foo': 0.75, u'bar': 0.80}

        filtered = Locator._filter_required(threshold, results)
        self.assertEqual(filtered, set([(1, None, u'foo', 0.80),
                                    (1, None, u'bar', 0.80)]))

        results = set([(0, None, u'foo', 0.7),
                   (1, None, u'bar', 0.7)])
        threshold = {u'foo': 0.8, u'bar': 0.8}

        filtered = Locator._filter_required(threshold, results)
        self.assertEqual(filtered, set())

    def test_filter_average(self):
        results = set([(0, None, u'foo', 0.0),
                   (0, None, u'bar', 1.0),
                   (1, None, u'foo', 0.8),
                   (1, None, u'bar', 0.6),
                   (2, None, u'foo', 0.0),
                   (2, None, u'bar', 0.0)])
        average = Locator._filter_average(results)
        self.assertEqual(average,
                         set([(0, None, frozenset([u'foo', u'bar']), 0.5),
                          (1, None, frozenset([u'foo', u'bar']), 0.7),
                          (2, None, frozenset([u'foo', u'bar']), 0.0)]))

        fn = lambda x: x.upper()
        results = set([(0, None, u'foo', 0.0),
                   (0, None, u'bar', 1.0),
                   (1, None, u'foo', 0.8),
                   (1, None, u'bar', 0.6),
                   (2, None, u'foo', 0.0),
                   (2, None, u'bar', 0.0),
                   (0, fn,   u'foo', 0.0),
                   (0, fn,   u'bar', 0.0),
                   (1, fn,   u'foo', 1.0),
                   (1, fn,   u'bar', 0.5),
                   (2, fn,   u'foo', 0.0),
                   (2, fn,   u'bar', 0.0)])
        average = Locator._filter_average(results)
        self.assertEqual(average,
                         set([(0, None, frozenset([u'foo', u'bar']), 0.50),
                          (1, None, frozenset([u'foo', u'bar']), 0.70),
                          (2, None, frozenset([u'foo', u'bar']), 0.00),
                          (0, fn,   frozenset([u'foo', u'bar']), 0.00),
                          (1, fn,   frozenset([u'foo', u'bar']), 0.75),
                          (2, fn,   frozenset([u'foo', u'bar']), 0.00)]))

    def test_filter_maximum(self):
        fn1 = lambda x: x.upper()
        fn2 = lambda x: x.lower()

        # Single max value, single objkey.
        results = set([(1, fn1,  frozenset([u'foo', u'bar']), 0.5),
                   (1, None, frozenset([u'foo', u'bar']), 0.7)])
        average = Locator._filter_maximum(results)
        self.assertEqual(average,
                         set([(1, None, frozenset([u'foo', u'bar']), 0.7)]))

        # Two-way tie for max value, single objkey.
        results = set([(1, fn1,  frozenset([u'foo', u'bar']), 0.5),
                   (1, fn2,  frozenset([u'foo', u'bar']), 0.7),
                   (1, None, frozenset([u'foo', u'bar']), 0.7)])
        average = Locator._filter_maximum(results)
        self.assertEqual(average,
                         set([(1, fn2,  frozenset([u'foo', u'bar']), 0.7),
                          (1, None, frozenset([u'foo', u'bar']), 0.7)]))

        # Single maximum value, multiple objkeys.
        results = set([(1, fn1,  frozenset([u'foo', u'bar']), 0.5),
                   (1, None, frozenset([u'foo', u'bar']), 0.7),
                   (2, fn1,  frozenset([u'foo', u'bar']), 0.6),
                   (2, None, frozenset([u'foo', u'bar']), 0.8)])
        average = Locator._filter_maximum(results)
        self.assertEqual(average,
                         set([(1, None, frozenset([u'foo', u'bar']), 0.7),
                          (2, None, frozenset([u'foo', u'bar']), 0.8)]))

        # Two-way ties for max value, multiple objkeys.
        results = set([(1, fn1,  frozenset([u'foo', u'bar']), 0.5),
                   (1, fn2,  frozenset([u'foo', u'bar']), 0.7),
                   (1, None, frozenset([u'foo', u'bar']), 0.7),
                   (2, fn1,  frozenset([u'foo', u'bar']), 0.9),
                   (2, fn2,  frozenset([u'foo', u'bar']), 0.9),
                   (2, None, frozenset([u'foo', u'bar']), 0.7)])
        average = Locator._filter_maximum(results)
        self.assertEqual(average,
                         set([(1, fn2,  frozenset([u'foo', u'bar']), 0.7),
                          (1, None, frozenset([u'foo', u'bar']), 0.7),
                          (2, fn1,  frozenset([u'foo', u'bar']), 0.9),
                          (2, fn2,  frozenset([u'foo', u'bar']), 0.9)]))

    def test_filter_order(self):
        fn1 = lambda x: x.upper()
        fn2 = lambda x: x.lower()

        # Single objkey, single adapter.
        results = set([(1, None, frozenset([u'foo', u'bar']), 0.7)])
        filtered = Locator._filter_order([None], results)
        self.assertEqual(filtered,
                         set([(1, None, frozenset([u'foo', u'bar']), 0.7)]))

        # Single objkey, multiple adapters (with NoneType first).
        results = set([(1, fn1,  frozenset([u'foo', u'bar']), 0.7),
                   (1, None, frozenset([u'foo', u'bar']), 0.7)])
        filtered = Locator._filter_order([None, fn1], results)
        self.assertEqual(filtered,
                         set([(1, None, frozenset([u'foo', u'bar']), 0.7)]))

        # Same as above but reversed order of adapters (with fn1 first).
        filtered = Locator._filter_order([fn1, None], results)
        self.assertEqual(filtered,
                         set([(1, fn1, frozenset([u'foo', u'bar']), 0.7)]))

        # Multiple objkeys, single adapter.
        results = set([(1, None, frozenset([u'foo', u'bar']), 0.7),
                   (2, None, frozenset([u'foo', u'bar']), 0.8)])
        filtered = Locator._filter_order([None], results)
        self.assertEqual(filtered,
                         set([(1, None, frozenset([u'foo', u'bar']), 0.7),
                          (2, None, frozenset([u'foo', u'bar']), 0.8)]))

        # Multiple objkeys, multiple adapters.
        results = set([(1, fn2,  frozenset([u'foo', u'bar']), 0.7),
                   (1, None, frozenset([u'foo', u'bar']), 0.7),
                   (2, fn1,  frozenset([u'foo', u'bar']), 0.9),
                   (2, fn2,  frozenset([u'foo', u'bar']), 0.9)])
        filtered = Locator._filter_order([None, fn1, fn2], results)
        self.assertEqual(filtered,
                         set([(1, None, frozenset([u'foo', u'bar']), 0.7),
                          (2, fn1,  frozenset([u'foo', u'bar']), 0.9)]))


class TestLocatorStateMethods(unittest.TestCase):
    def setUp(self):
        self.locate = Locator()
        self.locate.adapters  = [None]
        self.locate.threshold = {u'form': 0.75}
        self.locate.result    = set([(0, None, u'form', 0.0),
                                 (1, None, u'form', 0.8),
                                 (2, None, u'form', 0.7),
                                 (3, None, u'form', 0.0),
                                 (4, None, u'form', 0.0),
                                 (5, None, u'form', 0.0)])

    def test_get_matches(self):
        adapters = self.locate.adapters
        cutoff   = self.locate.threshold
        result   = self.locate.result

        matches = Locator._get_matches(adapters, cutoff, result)
        self.assertEqual(matches, set([(1, None, frozenset(set([u'form'])), 0.8)]))

        cutoff = {u'form': 0.7}
        matches = Locator._get_matches(adapters, cutoff, result)
        self.assertEqual(matches,
                         set([(1, None, frozenset(set([u'form'])), 0.8),
                          (2, None, frozenset(set([u'form'])), 0.7)]))

    def test_ismapped(self):
        self.locate.threshold = {u'form': 0.7}
        self.assertEqual(self.locate.ismapped(), False)  # ambiguous

        self.locate.threshold = {u'form': 0.75}
        self.assertEqual(self.locate.ismapped(), True)   # mapped

        self.locate.threshold = {u'form': 0.85}
        self.assertEqual(self.locate.ismapped(), False)  # unmapped


if __name__ == u'__main__':
    unittest.main()

