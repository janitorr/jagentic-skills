"""Price lookup with an optional cache."""

from .catalog import PRICES


class UnknownPrice(Exception):
    pass


def price(sku, region, currency, cache=None):
    if cache is not None:
        cached = cache.get(sku, region, currency)
        if cached is not None:
            return cached

    try:
        cents = PRICES[(sku, region, currency)]
    except KeyError as exc:
        raise UnknownPrice(f"no price for {(sku, region, currency)}") from exc

    if cache is not None:
        cache.put(sku, region, currency, cents)
    return cents
