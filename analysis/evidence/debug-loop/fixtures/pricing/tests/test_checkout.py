import unittest

from shop.cache import PriceCache
from shop.checkout import quote


class CheckoutQuoteTests(unittest.TestCase):
    def test_quote_without_cache(self):
        self.assertEqual(quote([("SKU-1", 1, "us-east", "USD")]), 1999)

    def test_quote_in_requested_currency(self):
        cache = PriceCache()
        self.assertEqual(quote([("SKU-1", 1, "us-east", "USD")], cache), 1999)
        self.assertEqual(quote([("SKU-1", 1, "us-east", "EUR")], cache), 1799)


if __name__ == "__main__":
    unittest.main()
