import unittest

from src.text import trim


class TestText(unittest.TestCase):
    def test_trim_removes_outer_whitespace(self):
        self.assertEqual(trim("  hello  "), "hello")
