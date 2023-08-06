
import adm._compatibility._unittest as unittest
from adm._compatibility._collections import namedtuple

from adm.partition import Cell


class TestBasics(unittest.TestCase):
    def test_getters(self):
        foo = Cell(u'Foo', 1)
        self.assertEqual(foo.label, u'Foo')
        self.assertEqual(foo.keys, (1,))
        self.assertIsNone(foo.adapter)

        fn = lambda x: x.upper()
        foo = Cell(u'Foo', 1, fn)
        self.assertEqual(foo.label, u'Foo')
        self.assertEqual(foo.keys, (1,))
        self.assertEqual(foo.adapter, fn)

    def test_setters(self):
        foo = Cell(u'Foo', 1)

        self.assertEqual(foo.keys, (1,))
        foo.keys = (2,)  # Uses setter.
        self.assertEqual(foo.keys, (2,))

        foo.keys = u'x'  # Uses setter.
        self.assertEqual(foo.keys, (u'x',))

        self.assertIsNone(foo.adapter)
        fn = lambda x: x.upper()
        foo.adapter = fn  # Uses setter.
        self.assertEqual(foo.adapter, fn)


class TestCellGraphFunctions(unittest.TestCase):
    def setUp(self):
        class MockCell(object):                            # Mocking to
            def __init__(self, label, *location, **kwds):  # avoid keys
                self.label = label                         # setter.
                self.keys = tuple(location)

        self.id_number  = MockCell(u'IdNumber',  0)
        self.first_name = MockCell(u'FirstName', 1)
        self.last_name  = MockCell(u'LastName',  2)
        self.full_name  = \
            MockCell(u'FullName', self.first_name, self.last_name)
        self.person     = \
            MockCell(u'Person',   self.id_number,  self.full_name)
        # Graph of Cells:
        #
        #        person
        #        /    \
        # id_number  full_name
        #   /          /     \
        #  0  first_name   last_name
        #        /               \
        #       1                 2

    def test_get_digraph(self):
        graph = Cell._get_digraph(self.person)
        self.assertEqual(graph, [(self.person,     self.id_number),
                                 (self.id_number,  0),
                                 (self.person,     self.full_name),
                                 (self.full_name,  self.first_name),
                                 (self.first_name, 1),
                                 (self.full_name,  self.last_name),
                                 (self.last_name,  2)])

    def test_get_leaf_arcs(self):
        digraph = [(self.person,     self.id_number),
                   (self.id_number,  0),
                   (self.person,     self.full_name),
                   (self.full_name,  self.first_name),
                   (self.first_name, 1),
                   (self.full_name,  self.last_name),
                   (self.last_name,  2)]

        leaves = Cell._get_leaf_arcs(digraph)

        self.assertEqual(leaves, [(self.id_number,  0),
                                  (self.first_name, 1),
                                  (self.last_name,  2)])

    def test_get_orphan_arcs(self):
        digraph = [(self.person,     self.id_number),
                   (self.id_number,  0),
                   (self.person,     self.full_name),
                   (self.full_name,  self.first_name),
                   (self.first_name, 1),
                   (self.full_name,  self.last_name),
                   (self.last_name,  2)]

        orphans = Cell._get_orphan_arcs(digraph)

        self.assertEqual(orphans, [(self.person, self.id_number),
                                   (self.person, self.full_name)])

    def test_valid_chain(self):
        Cell._validate_chain(self.person)  # Chain is finite.


class TestCellValidateChain(unittest.TestCase):
    def test_directly(self):
        class MockCell(object):                            # Mocking to
            def __init__(self, label, *location, **kwds):  # avoid keys
                self.label = label                         # setter.
                self.keys = tuple(location)

        bar   = MockCell(u'Bar',   0)          #       Foo
        qux   = MockCell(u'Qux',   1)          #      /   \
        corge = MockCell(u'Corge', None)       #    Bar   Baz <---
        quux  = MockCell(u'Quux',  corge)      #   /      /  \    \
        baz   = MockCell(u'Baz',   qux, quux)  #  0     Qux   Quux |
        foo   = MockCell(u'Foo',   bar, baz)   #        /       \  |
        corge.keys = (baz,)                   #       1        Corge

        def infinitechain():
            Cell._validate_chain(foo)
        pattern = (u'violates finite chain condition: Baz->Quux, '
                   u'Quux->Corge, Corge->Baz')
        self.assertRaisesRegex(AttributeError, pattern, infinitechain)

    def test_through_setter(self):        # Initial graph of Cells:
        bar   = Cell(u'Bar',   0)          #
        qux   = Cell(u'Qux',   1)          #       foo
        corge = Cell(u'Corge', 2)          #      /   \
        quux  = Cell(u'Quux',  corge)      #    bar   baz
        baz   = Cell(u'Baz',   qux, quux)  #    /     /  \
        foo   = Cell(u'Foo',   bar, baz)   #   0    qux   quux
                                          #        /       \
                                          #       1       corge
                                          #                  \
        def infinitechain():              #                   2
            corge.keys = (baz,)
            # This assignment changes the graph causing it to loop
            # back on itself which results in an infinite chain.
        pattern = (u'violates finite chain condition: Corge->Baz, '
                   u'Baz->Quux, Quux->Corge')
        self.assertRaisesRegex(AttributeError, pattern, infinitechain)


class TestCellInitAndAssignment(unittest.TestCase):
    def test_init(self):
        foo = Cell(u'Foo', 0)  # Simple location
        self.assertEqual(foo.label, u'Foo')
        self.assertEqual(foo.keys, (0,))
        self.assertIsNone(foo.adapter)

        bar = Cell(u'Bar', u'first_name', u'last_name')  # Compound location
        self.assertEqual(bar.label, u'Bar')
        self.assertEqual(bar.keys, (u'first_name', u'last_name'))
        self.assertIsNone(bar.adapter)

        baz = Cell(u'Baz', keys=0)  # Keyword location
        self.assertEqual(baz.label, u'Baz')
        self.assertEqual(baz.keys, (0,))
        self.assertIsNone(baz.adapter)

        fn = lambda x: x.strip()  # Inlined adapter
        qux = Cell(u'Qux', 0, fn)
        self.assertEqual(qux.label, u'Qux')
        self.assertEqual(qux.keys, (0,))
        self.assertEqual(qux.adapter, fn)

        def missinglocation():
            quux = Cell(u'Quux')
        pattern = u'keys are required \(none provided\)'
        self.assertRaisesRegex(AttributeError, pattern, missinglocation)

    def test_assignment(self):
        foo = Cell(u'Foo', 0)

        fn = lambda x: x.upper()
        foo.adapter = fn                              # Setter
        self.assertEqual(foo.adapter, fn)

        foo.adapter = None                            # Setter
        self.assertIsNone(foo.adapter)

        foo.keys = 1                                  # Setter
        self.assertEqual(foo.keys, (1,))

        foo.keys = [2]                                # Setter
        self.assertEqual(foo.keys, (2,))

        def atleast2gives1():
            foo.adapter = lambda x,y,z=None: (x,y,z)  # Setter
        self.assertRaises(AttributeError, atleast2gives1)

        def uncallable():
            foo.adapter = u'uncallable string'         # Setter
        self.assertRaises(TypeError, uncallable)


class TestCellCall(unittest.TestCase):
    def setUp(self):
        self.samplerow = [u'John', u'Smith', u'(546) 234-2344']

    def test_simple(self):
        phone = Cell(u'PhoneNumber', 2)
        self.assertEqual(phone(self.samplerow), u'(546) 234-2344')

    def test_simple_adapter(self):
        firstname = Cell(u'FirstName', 0, adapter=lambda x: x.upper())
        self.assertEqual(firstname(self.samplerow), u'JOHN')

    def test_composite(self):
        fullname = Cell(u'FullName', 0, 1)
        self.assertEqual(fullname(self.samplerow), {0: u'John',
                                                    1: u'Smith'})

    def test_composite_adapter(self):
        fullname = Cell(u'FullName', 0, 1, adapter=lambda x,y: x+u' '+y)
        self.assertEqual(fullname(self.samplerow), u'John Smith')

    def test_nested(self):
        concat = lambda *x: u' '.join(x)
        mapper = Cell(u'ContactInfo',
                      Cell(u'FullName',
                           Cell(u'FirstName', 0),
                           Cell(u'LastName',  1),
                           adapter=concat),
                      Cell(u'PhoneNumber', 2))
        self.assertEqual(mapper(self.samplerow),
                         {u'FullName': u'John Smith',
                          u'PhoneNumber': u'(546) 234-2344'})

    def test_redundant_leaf(self):                 # Graph of Cells:
        mapper = Cell(u'FullName',                  #
                      Cell(u'FirstName',            #      FullName
                           Cell(u'GivenName', 0)),  #       /     \
                      Cell(u'LastName', 1))         # FirstName  LastName
                                                   #     |         |
                                                   # GivenName     1
        result = mapper(self.samplerow)            #     |
        self.assertEqual(result,                   #     0
                         {u'FirstName': u'John', u'LastName': u'Smith'})
        # In this graph, FirstName and GivenName are structurally
        # redundant.  Redundancy of this type should be collapsed into
        # a single cell when generating mapped results.  In this case,
        # GivenName is collapsed into FirstName.  The mapped result
        # shows that the key 'FirstName' is directly paired with the
        # value in index 0 ('John') -- GivenName is not used.

    def test_redundant_root(self):                 # Graph of Cells:
        mapper = Cell(u'FullName',                  #
                      Cell(u'PersonalName',         #      FullName
                           Cell(u'FirstName', 0),   #         |
                           Cell(u'LastName',  1)))  #    PersonalName
                                                   #       /     \
                                                   # FirstName  LastName
        result = mapper(self.samplerow)            #     |         |
        self.assertEqual(result,                   #     0         1
                         {u'FirstName': u'John', u'LastName': u'Smith'})
        # In this graph, FullName and PersonalName are structurally
        # redundant.  Redundancy of this type should be collapsed into
        # a single cell when generating mapped results.  In this case,
        # PersonalName is collapsed into FullName.

    def test_failed_location(self):
        mapper = Cell(u'FullName',
                      Cell(u'FirstName', None),
                      Cell(u'LastName', 1))
        result = mapper(self.samplerow)
        self.assertEqual(result, {u'FirstName': None,
                                  u'LastName': u'Smith'})


class TestCellMaptypes(unittest.TestCase):
    def setUp(self):
        self.samplerow = [u'John', u'Smith', u'(546) 234-2344']
        self.mapper = Cell(u'ContactInfo',
                      Cell(u'FullName',
                           Cell(u'FirstName', 0),
                           Cell(u'LastName',  1)),
                      Cell(u'PhoneNumber', 2))

    def test_maptype_list(self):
        result = self.mapper(self.samplerow, maptype=list)
        self.assertEqual(result, [[u'John', u'Smith'], u'(546) 234-2344'])

    def test_maptype_namedtuple(self):
        ContactInfo = namedtuple(u'ContactInfo',
                                 [u'FullName', u'PhoneNumber'])
        FullName = namedtuple(u'FullName', [u'FirstName', u'LastName'])

        result = self.mapper(self.samplerow, maptype=namedtuple)
        self.assertEqual(result,
               ContactInfo(FullName(u'John', u'Smith'), u'(546) 234-2344'))
        self.assertEqual(result.FullName, FullName(u'John', u'Smith'))
        self.assertEqual(result.FullName.FirstName, u'John')
        self.assertEqual(result.FullName.LastName, u'Smith')
        self.assertEqual(result.PhoneNumber, u'(546) 234-2344')


if __name__ == u'__main__':
    unittest.main()

