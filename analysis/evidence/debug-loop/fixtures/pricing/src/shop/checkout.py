"""Checkout quotes."""

from .pricing import price


def quote(lines, cache=None):
    total = 0
    for sku, quantity, region, currency in lines:
        total += price(sku, region, currency, cache) * quantity
    return total
