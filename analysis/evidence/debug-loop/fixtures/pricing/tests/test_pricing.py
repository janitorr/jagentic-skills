import unittest

from shop.pricing import UnknownPrice, price


class PricingTests(unittest.TestCase):
    def test_price_without_cache(self):
        self.assertEqual(price("SKU-1", "us-east", "EUR"), 1799)

    def test_unknown_price_raises(self):
        with self.assertRaises(UnknownPrice):
            price("SKU-9", "us-east", "USD")


if __name__ == "__main__":
    unittest.main()
