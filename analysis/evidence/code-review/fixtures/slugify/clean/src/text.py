import re


def trim(text: str) -> str:
    return text.strip()


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w\s]|_", "", text.strip().lower())
    return re.sub(r"\s+", "-", cleaned).strip("-")
