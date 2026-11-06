"""Invoice helpers that share the money conversion."""

from .money import to_cents


def invoice_total(amounts):
    return sum(to_cents(amount) for amount in amounts)
