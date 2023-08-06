
import adm._compatibility._unittest as unittest
from adm._compatibility._collections import namedtuple

from adm import Cell
from adm import Locator
from adm import Location


class TestLocatorLocation(unittest.TestCase):
    def test_get_location(self):
        locate = Locator()
        locate.result = set([(1, None, u'foo', 0.8),
                         (2, None, u'foo', 0.7)])

        locate.threshold = {u'foo': 0.65}
        self.assertEqual(locate.location(), set([Location(1), Location(2)]))

        locate.threshold = {u'foo': 0.75}
        self.assertEqual(locate.location(), Location(1))

        locate.threshold = {u'foo': 0.85}
        self.assertEqual(locate.location(), None)

    def test_call_locator(self):
        u"""Calling a Locator will, in-turn, build and call a Location
        object (if the Locator is mapped)."""
        locate = Locator()
        locate.result = set([(1, None, u'form', 0.8)])

        row = [u'foo', u'bar', u'baz']

        locate.threshold = {u'form': 0.8}
        self.assertEqual(locate(row), u'bar')

        locate.threshold = {u'form': 0.9}
        self.assertEqual(locate(row), None)


class TestCellLocationLocator(unittest.TestCase):
    u"""Test interaction of Cell, Location, and Locator objects."""

    def test_ismapped(self):
        mapper = Cell(u'foo', 0)
        self.assertEqual(mapper._ismapped(), True)  # Literal val keys.

        mapper = Cell(u'foo', u'column_0')
        self.assertEqual(mapper._ismapped(), True)  # Literal val keys.

        mapper = Cell(u'foo', Location(0))
        self.assertEqual(mapper._ismapped(), True)  # Location keys.

        mapper = Cell(u'foo', Cell(u'bar', 0))
        self.assertEqual(mapper._ismapped(), True)  # Chained Cell keys.

        locator = Locator()
        locator.result = set([(0, None, u'form', 0.8)])
        mapper = Cell(u'foo', locator)  # Mapper using Locator keys.

        locator.threshold = {u'form': 0.85}  # Result < cutoff.
        self.assertEqual(mapper._ismapped(), False)

        locator.threshold = {u'form': 0.75}  # Result > cutoff.
        self.assertEqual(mapper._ismapped(), True)

    def test_mapped_unmapped(self):
        mapper = Cell(u'contact_info',
                      Cell(u'first_name', 0),
                      Cell(u'last_name',  1),
                      Cell(u'phone',      2))
        self.assertEqual(mapper.mapped(),
                         set([u'first_name', u'last_name', u'phone']))

        mapper = Cell(u'contact_info',
                      Cell(u'first_name', Location(0)),
                      Cell(u'last_name',  Location(1)),
                      Cell(u'phone',      Location(2)))
        self.assertEqual(mapper.mapped(),
                         set([u'first_name', u'last_name', u'phone']))

        #
        locator = Locator()
        locator.result = set([(2, None, u'form', 0.8)])
        mapper = Cell(u'contact_info',
                      Cell(u'first_name', 0),            # Literal value.
                      Cell(u'last_name',  Location(1)),  # Location obj.
                      Cell(u'phone',      locator))      # Locator obj.

        locator.threshold = {u'form': 0.85}  # Result < cutoff.
        self.assertEqual(mapper.mapped(), set([u'first_name', u'last_name']))
        self.assertEqual(mapper.unmapped(), set([u'phone']))


        locator.threshold = {u'form': 0.75}  # Result > cutoff.
        self.assertEqual(mapper.mapped(),
                         set([u'first_name', u'last_name', u'phone']))
        self.assertEqual(mapper.unmapped(), set())



class TestCellLocationLocatorHacks(unittest.TestCase):
    def test_foo(self):

        def begin2space(x):
            if u' ' in x:
                return x[:x.index(u' ')].strip()
            return u''

        def space2end(x):
            if u' ' in x:
                return x[x.rindex(u' ')+1:].strip()
            return u''

        def comma2end(x):
            if u', ' in x:
                return x[x.rindex(u', ')+1:]
            return u''

        def begin2comma(x):
            if u',' in x:
                return x[:x.rindex(u',')]
            return u''

        fname = Locator(None, begin2comma, comma2end, begin2space,
                        space2end, form=ur'^[JAR][a-z]*$')
        lname = Locator(None, begin2comma, comma2end, begin2space,
                        space2end, form=ur'^[SLC][a-z]*$')
        phone = Locator(form=ur'^[^\d]*\d{3}[^\d]*\d{3}[^\d]*\d{4}[^\d]*$')

        mapper = Cell(u'contact_info',
                      Cell(u'first_name', fname),
                      Cell(u'last_name',  lname),
                      Cell(u'phone',      phone))

        samp1 = [[u'John Smith',     u'', u'408-443-3333', u'', u'', u'', u''],
                 [u'Abe Lincoln',    u'', u'317-746-2235', u'', u'', u'', u''],
                 [u'Rachal Summers', u'', u'3/09/12',      u'', u'', u'', u''],
                 [u'Jeff Coomb',     u'', u'219-282-4981', u'', u'', u'', u''],
                 [u'Audrey Laskin',  u'', u'301-639-2028', u'', u'', u'', u'']]

        samp2 = [[u'', u'Smith, John',     u'', u'408-443-3333', u'', u'', u''],
                 [u'', u'Lincoln, Abe',    u'', u'317-746-2235', u'', u'', u''],
                 [u'', u'Summers, Rachal', u'', u'3/09/12',      u'', u'', u''],
                 [u'', u'Coomb, Jeff',     u'', u'219-282-4981', u'', u'', u''],
                 [u'', u'Laskin, Audrey',  u'', u'301-639-2028', u'', u'', u'']]

        samp3 = [[u'', u'', u'', u'John',   u'Smith',   u'(408) 443-3333', u''],
                 [u'', u'', u'', u'Abe',    u'Lincoln', u'317.746.2235',   u''],
                 [u'', u'', u'', u'Rachal', u'Summers', u'3/09/12',        u''],
                 [u'', u'', u'', u'Jeff',   u'Coomb',   u'2192824981',     u''],
                 [u'', u'', u'', u'Audrey', u'Laskin',  u'301-639-2028',   u'']]

        samp4 = [[u'', u'', u'Smith, John', u'', u'Xohn',   u'Smith',       u'(408) 443-3333', u''],
                 [u'', u'', u'Lincoln, Abe', u'', u'Abe',    u'Lincoln',    u'317.746.2235',   u''],
                 [u'', u'', u'Summers, Rachal', u'', u'Xachal', u'Summers', u'3/09/12',        u''],
                 [u'', u'', u'Coomb, Jeff', u'', u'Jeff',   u'Coomb',       u'2192824981',     u''],
                 [u'', u'', u'Laskin, Audrey', u'', u'Audrey', u'Laskin',   u'301-639-2028',   u'']]

        #from collections import OrderedDict
        sample = samp4
        mapper.identify(sample, form=0.75)
        #for x in mapper.keys[0].keys[0].result:
        #    print(x)

        print mapper.keys[0].keys[0]
        print
        #print(mapper.keys[1].keys[0])
        print mapper
        print u'  MAPPED:', mapper.mapped()
        print u'UNMAPPED:', mapper.unmapped()
        for row in sample:
            print row
            pass

        for row in sample:
            print mapper(row, namedtuple)
            #print(mapper(row))
            pass

            #row = mapper(row, namedtuple)
            #row = mapper(row, OrderedDict)
            #row = mapper(row, tuple)
            #row = mapper(row)
            #row = mapper(row, list)
            #print(row.first_name, row.last_name, row.phone)


TestCellLocationLocatorHacks = unittest.skip(TestCellLocationLocatorHacks)
if __name__ == u'__main__':
    unittest.main()

