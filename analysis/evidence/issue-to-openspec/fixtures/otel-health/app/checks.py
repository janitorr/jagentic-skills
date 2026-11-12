import os


def database_ready() -> bool:
    return os.getenv("DATABASE_READY", "1") == "1"


def cache_ready() -> bool:
    return os.getenv("CACHE_READY", "1") == "1"
