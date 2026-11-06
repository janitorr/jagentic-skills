"""Parse order lines into records."""

from .money import to_cents


def parse_amount(text):
    """Parse a decimal amount string into integer cents."""
    return to_cents(text)


def parse_row(line):
    date, description, amount, category = [field.strip() for field in line.split(",")]
    return {
        "date": date,
        "description": description,
        "amount_cents": parse_amount(amount),
        "category": category,
    }


def parse_lines(lines):
    return [parse_row(line) for line in lines if line.strip()]
