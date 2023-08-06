
import adm._compatibility._unittest as unittest
from adm._compatibility._collections import namedtuple

from adm import Cell
from adm import Locator
from adm import Location


class TestLocatorLocation(unittest.TestCase):
    def test_get_location(self):
        locate = Locator()
        locate.result = {(1, None, 'foo', 0.8),
                         (2, None, 'foo', 0.7)}

        locate.threshold = {'foo': 0.65}
        self.assertEqual(locate.location(), {Location(1), Location(2)})

        locate.threshold = {'foo': 0.75}
        self.assertEqual(locate.location(), Location(1))

        locate.threshold = {'foo': 0.85}
        self.assertEqual(locate.location(), None)

    def test_call_locator(self):
        """Calling a Locator will, in-turn, build and call a Location
        object (if the Locator is mapped)."""
        locate = Locator()
        locate.result = {(1, None, 'form', 0.8)}

        row = ['foo', 'bar', 'baz']

        locate.threshold = {'form': 0.8}
        self.assertEqual(locate(row), 'bar')

        locate.threshold = {'form': 0.9}
        self.assertEqual(locate(row), None)


class TestCellLocationLocator(unittest.TestCase):
    """Test interaction of Cell, Location, and Locator objects."""

    def test_ismapped(self):
        mapper = Cell('foo', 0)
        self.assertEqual(mapper._ismapped(), True)  # Literal val keys.

        mapper = Cell('foo', 'column_0')
        self.assertEqual(mapper._ismapped(), True)  # Literal val keys.

        mapper = Cell('foo', Location(0))
        self.assertEqual(mapper._ismapped(), True)  # Location keys.

        mapper = Cell('foo', Cell('bar', 0))
        self.assertEqual(mapper._ismapped(), True)  # Chained Cell keys.

        locator = Locator()
        locator.result = {(0, None, 'form', 0.8)}
        mapper = Cell('foo', locator)  # Mapper using Locator keys.

        locator.threshold = {'form': 0.85}  # Result < cutoff.
        self.assertEqual(mapper._ismapped(), False)

        locator.threshold = {'form': 0.75}  # Result > cutoff.
        self.assertEqual(mapper._ismapped(), True)

    def test_mapped_unmapped(self):
        mapper = Cell('contact_info',
                      Cell('first_name', 0),
                      Cell('last_name',  1),
                      Cell('phone',      2))
        self.assertEqual(mapper.mapped(),
                         {'first_name', 'last_name', 'phone'})

        mapper = Cell('contact_info',
                      Cell('first_name', Location(0)),
                      Cell('last_name',  Location(1)),
                      Cell('phone',      Location(2)))
        self.assertEqual(mapper.mapped(),
                         {'first_name', 'last_name', 'phone'})

        #
        locator = Locator()
        locator.result = {(2, None, 'form', 0.8)}
        mapper = Cell('contact_info',
                      Cell('first_name', 0),            # Literal value.
                      Cell('last_name',  Location(1)),  # Location obj.
                      Cell('phone',      locator))      # Locator obj.

        locator.threshold = {'form': 0.85}  # Result < cutoff.
        self.assertEqual(mapper.mapped(), {'first_name', 'last_name'})
        self.assertEqual(mapper.unmapped(), {'phone'})


        locator.threshold = {'form': 0.75}  # Result > cutoff.
        self.assertEqual(mapper.mapped(),
                         {'first_name', 'last_name', 'phone'})
        self.assertEqual(mapper.unmapped(), set())



@unittest.skip
class TestCellLocationLocatorHacks(unittest.TestCase):
    def test_foo(self):

        def begin2space(x):
            if ' ' in x:
                return x[:x.index(' ')].strip()
            return ''

        def space2end(x):
            if ' ' in x:
                return x[x.rindex(' ')+1:].strip()
            return ''

        def comma2end(x):
            if ', ' in x:
                return x[x.rindex(', ')+1:]
            return ''

        def begin2comma(x):
            if ',' in x:
                return x[:x.rindex(',')]
            return ''

        fname = Locator(None, begin2comma, comma2end, begin2space,
                        space2end, form=r'^[JAR][a-z]*$')
        lname = Locator(None, begin2comma, comma2end, begin2space,
                        space2end, form=r'^[SLC][a-z]*$')
        phone = Locator(form=r'^[^\d]*\d{3}[^\d]*\d{3}[^\d]*\d{4}[^\d]*$')

        mapper = Cell('contact_info',
                      Cell('first_name', fname),
                      Cell('last_name',  lname),
                      Cell('phone',      phone))

        samp1 = [['John Smith',     '', '408-443-3333', '', '', '', ''],
                 ['Abe Lincoln',    '', '317-746-2235', '', '', '', ''],
                 ['Rachal Summers', '', '3/09/12',      '', '', '', ''],
                 ['Jeff Coomb',     '', '219-282-4981', '', '', '', ''],
                 ['Audrey Laskin',  '', '301-639-2028', '', '', '', '']]

        samp2 = [['', 'Smith, John',     '', '408-443-3333', '', '', ''],
                 ['', 'Lincoln, Abe',    '', '317-746-2235', '', '', ''],
                 ['', 'Summers, Rachal', '', '3/09/12',      '', '', ''],
                 ['', 'Coomb, Jeff',     '', '219-282-4981', '', '', ''],
                 ['', 'Laskin, Audrey',  '', '301-639-2028', '', '', '']]

        samp3 = [['', '', '', 'John',   'Smith',   '(408) 443-3333', ''],
                 ['', '', '', 'Abe',    'Lincoln', '317.746.2235',   ''],
                 ['', '', '', 'Rachal', 'Summers', '3/09/12',        ''],
                 ['', '', '', 'Jeff',   'Coomb',   '2192824981',     ''],
                 ['', '', '', 'Audrey', 'Laskin',  '301-639-2028',   '']]

        samp4 = [['', '', 'Smith, John', '', 'Xohn',   'Smith',       '(408) 443-3333', ''],
                 ['', '', 'Lincoln, Abe', '', 'Abe',    'Lincoln',    '317.746.2235',   ''],
                 ['', '', 'Summers, Rachal', '', 'Xachal', 'Summers', '3/09/12',        ''],
                 ['', '', 'Coomb, Jeff', '', 'Jeff',   'Coomb',       '2192824981',     ''],
                 ['', '', 'Laskin, Audrey', '', 'Audrey', 'Laskin',   '301-639-2028',   '']]

        #from collections import OrderedDict
        sample = samp4
        mapper.identify(sample, form=0.75)
        #for x in mapper.keys[0].keys[0].result:
        #    print(x)

        print(mapper.keys[0].keys[0])
        print()
        #print(mapper.keys[1].keys[0])
        print(mapper)
        print('  MAPPED:', mapper.mapped())
        print('UNMAPPED:', mapper.unmapped())
        for row in sample:
            print(row)
            pass

        for row in sample:
            print(mapper(row, namedtuple))
            #print(mapper(row))
            pass

            #row = mapper(row, namedtuple)
            #row = mapper(row, OrderedDict)
            #row = mapper(row, tuple)
            #row = mapper(row)
            #row = mapper(row, list)
            #print(row.first_name, row.last_name, row.phone)


if __name__ == '__main__':
    unittest.main()

