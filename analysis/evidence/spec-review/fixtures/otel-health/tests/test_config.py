import unittest

from app.config import service_name


class ServiceNameTest(unittest.TestCase):
    def test_service_name(self) -> None:
        self.assertEqual(service_name(), "orders-api")


if __name__ == "__main__":
    unittest.main()
