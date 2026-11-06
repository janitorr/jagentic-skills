import unittest

from orders.parse import parse_amount


class ParseAmountTests(unittest.TestCase):
    def test_whole_dollars(self):
        self.assertEqual(parse_amount("42.00"), 4200)

    def test_small_amount(self):
        self.assertEqual(parse_amount("1.15"), 115)


if __name__ == "__main__":
    unittest.main()
