"""Outbound webhook delivery."""


class WebhookSender:
    """Sends one delivery attempt. The transport raises on failure."""

    def __init__(self, http_client):
        self._http = http_client

    def send(self, url, payload):
        response = self._http.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.status_code
