import unittest

from orders.invoice import invoice_total
from orders.money import to_cents


class RootCauseTests(unittest.TestCase):
    def test_conversion_rounds_to_nearest_cent(self):
        self.assertEqual(to_cents("1.15"), 115)
        self.assertEqual(to_cents("19.99"), 1999)

    def test_second_caller_gets_the_same_fix(self):
        self.assertEqual(invoice_total(["1.15", "19.99"]), 2114)


if __name__ == "__main__":
    unittest.main()
