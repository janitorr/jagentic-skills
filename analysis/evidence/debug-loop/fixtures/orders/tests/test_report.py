import unittest

from orders.parse import parse_lines
from orders.report import total_by_category


class ReportTests(unittest.TestCase):
    def test_total_by_category(self):
        rows = parse_lines(
            [
                "2026-01-02,Coffee,4.50,food",
                "2026-01-03,Tea,2.75,food",
            ]
        )
        self.assertEqual(total_by_category(rows), {"food": 725})

    def test_total_with_awkward_cents(self):
        rows = parse_lines(["2026-01-04,Snack,1.15,food"])
        self.assertEqual(total_by_category(rows), {"food": 115})


if __name__ == "__main__":
    unittest.main()
