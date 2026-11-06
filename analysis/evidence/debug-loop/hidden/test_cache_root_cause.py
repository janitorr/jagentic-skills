import unittest

from shop.cache import PriceCache
from shop.invoice import invoice_total
from shop.pricing import price


class CacheRootCauseTests(unittest.TestCase):
    def test_currency_is_part_of_the_cache_key(self):
        cache = PriceCache()
        self.assertEqual(price("SKU-1", "us-east", "USD", cache), 1999)
        self.assertEqual(price("SKU-1", "us-east", "EUR", cache), 1799)

    def test_second_caller_gets_the_same_fix(self):
        cache = PriceCache()
        self.assertEqual(
            invoice_total([("SKU-1", 1, "us-east", "USD")], cache), 1999
        )
        self.assertEqual(
            invoice_total([("SKU-1", 1, "us-east", "EUR")], cache), 1799
        )

    def test_region_is_still_part_of_the_key(self):
        cache = PriceCache()
        self.assertEqual(price("SKU-1", "us-east", "EUR", cache), 1799)
        self.assertEqual(price("SKU-1", "eu-west", "EUR", cache), 1849)


if __name__ == "__main__":
    unittest.main()
