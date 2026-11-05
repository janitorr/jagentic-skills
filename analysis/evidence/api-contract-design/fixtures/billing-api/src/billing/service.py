"""Internal billing service. No HTTP layer exists yet."""

from .models import Invoice, Payment


class NotFound(Exception):
    pass


class InvalidState(Exception):
    pass


class BillingService:
    def __init__(self, db, provider):
        self.db = db
        self.provider = provider

    def list_invoices(
        self,
        customer_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Invoice]:
        """Return invoices. The admin tool asks for the newest first."""
        raise NotImplementedError

    def get_invoice(self, invoice_id: str) -> Invoice:
        raise NotImplementedError

    def create_draft(self, customer_id: str, lines: list[dict]) -> Invoice:
        raise NotImplementedError

    def update_draft(self, invoice_id: str, patch: dict) -> Invoice:
        """Patch lines, description, or currency. Callers send only what changed."""
        raise NotImplementedError

    def charge(
        self,
        invoice_id: str,
        amount_cents: int,
        currency: str,
        payment_method_token: str,
    ) -> Payment:
        """Charge through the external provider.

        The provider call can take 30 seconds. A timeout does not tell us whether
        the charge was applied. The provider response is external JSON.
        """
        raise NotImplementedError
