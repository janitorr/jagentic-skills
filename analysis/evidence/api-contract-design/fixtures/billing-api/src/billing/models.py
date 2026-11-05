from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class InvoiceLine:
    id: str
    description: str
    quantity: int
    unit_amount_cents: int
    position: int


@dataclass
class Invoice:
    id: str
    tenant_id: str
    customer_id: str
    status: str
    currency: str
    version: int
    created_at: datetime
    updated_at: datetime
    lines: list[InvoiceLine] = field(default_factory=list)


@dataclass
class Payment:
    id: str
    tenant_id: str
    invoice_id: str
    amount_cents: int
    currency: str
    status: str
    provider_charge_id: str | None
    created_at: datetime
    updated_at: datetime
