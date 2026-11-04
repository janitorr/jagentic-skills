import unittest

from src.delivery import WebhookSender
from src.notifications import OrderNotifier


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeClient:
    def __init__(self, status_codes):
        self.status_codes = list(status_codes)
        self.calls = []

    def post(self, url, json, timeout):
        self.calls.append((url, json))
        return FakeResponse(self.status_codes.pop(0))


class WebhookSenderTest(unittest.TestCase):
    def test_send_posts_once(self):
        client = FakeClient([200])
        sender = WebhookSender(client)

        self.assertEqual(sender.send("https://example.test/hook", {"id": 1}), 200)
        self.assertEqual(len(client.calls), 1)

    def test_send_raises_on_http_error(self):
        client = FakeClient([503])
        sender = WebhookSender(client)

        with self.assertRaises(RuntimeError):
            sender.send("https://example.test/hook", {"id": 1})


class OrderNotifierTest(unittest.TestCase):
    def test_order_created_uses_sender(self):
        client = FakeClient([200])
        notifier = OrderNotifier(WebhookSender(client), "https://example.test/hook")

        notifier.order_created({"id": "o-1"})

        self.assertEqual(client.calls[0][1], {"event": "order.created", "id": "o-1"})


if __name__ == "__main__":
    unittest.main()
