import unittest

from shop.cache import PriceCache
from shop.invoice import invoice_total


class InvoiceTests(unittest.TestCase):
    def test_invoice_total(self):
        self.assertEqual(
            invoice_total([("SKU-1", 1, "us-east", "USD")]), 1999
        )

    def test_invoice_total_with_a_cache(self):
        cache = PriceCache()
        self.assertEqual(
            invoice_total([("SKU-1", 1, "us-east", "USD")], cache), 1999
        )


if __name__ == "__main__":
    unittest.main()
