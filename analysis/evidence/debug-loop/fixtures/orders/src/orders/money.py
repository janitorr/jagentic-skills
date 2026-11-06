"""Money conversion helpers."""


def to_cents(text):
    """Convert a decimal money string into integer cents."""
    return int(float(text) * 100)
