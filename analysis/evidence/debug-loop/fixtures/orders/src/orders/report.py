"""Summarize parsed order records."""

from collections import defaultdict


def total_by_category(rows):
    totals = defaultdict(int)
    for row in rows:
        totals[row["category"]] += row["amount_cents"]
    return dict(totals)
