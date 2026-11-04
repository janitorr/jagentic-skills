"""Event notifications sent to partner webhooks."""


class OrderNotifier:
    def __init__(self, sender, webhook_url):
        self._sender = sender
        self._url = webhook_url

    def order_created(self, order):
        return self._sender.send(self._url, {"event": "order.created", "id": order["id"]})


class InvoiceNotifier:
    def __init__(self, sender, webhook_url):
        self._sender = sender
        self._url = webhook_url

    def invoice_paid(self, invoice):
        return self._sender.send(self._url, {"event": "invoice.paid", "id": invoice["id"]})


class RefundNotifier:
    def __init__(self, sender, webhook_url):
        self._sender = sender
        self._url = webhook_url

    def refund_issued(self, refund):
        return self._sender.send(self._url, {"event": "refund.issued", "id": refund["id"]})
