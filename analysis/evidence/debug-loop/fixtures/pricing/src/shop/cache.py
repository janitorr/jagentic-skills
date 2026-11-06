"""A small in-process price cache."""


class PriceCache:
    def __init__(self):
        self._prices = {}

    def key(self, sku, region, currency):
        # Currency is normalised by the caller; sku and region identify a price.
        return (sku, region)

    def get(self, sku, region, currency):
        return self._prices.get(self.key(sku, region, currency))

    def put(self, sku, region, currency, cents):
        self._prices[self.key(sku, region, currency)] = cents
