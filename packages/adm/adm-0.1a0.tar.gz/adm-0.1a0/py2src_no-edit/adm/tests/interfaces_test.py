
import adm._compatibility._unittest as unittest

from adm._interfaces import _is_hashable
from adm._interfaces import _is_sequence
from adm._interfaces import _is_mapping


class TestInterfaceChecking(unittest.TestCase):
    def test_is_hashable(self):
        self.assertTrue(_is_hashable(1))
        self.assertFalse(_is_hashable([]))

    def test_is_container(self):
        pass  # TODO: Add this test.

    def test_is_sequence(self):
        self.assertTrue(_is_sequence([1,2,3]))
        self.assertFalse(_is_sequence(set([1,2,3])))

    def test_is_mapping(self):
        self.assertTrue(_is_mapping({u'a': 1, u'b': 2, u'c': 3}))
        self.assertFalse(_is_mapping([1,2,3]))


if __name__ == u'__main__':
    unittest.main()

