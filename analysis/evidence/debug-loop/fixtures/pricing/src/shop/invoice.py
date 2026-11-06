"""Invoice lines, sharing the same price lookup."""

from .pricing import price


def invoice_lines(lines, cache=None):
    return [
        {
            "sku": sku,
            "quantity": quantity,
            "cents": price(sku, region, currency, cache) * quantity,
        }
        for sku, quantity, region, currency in lines
    ]


def invoice_total(lines, cache=None):
    return sum(line["cents"] for line in invoice_lines(lines, cache))
