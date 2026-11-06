import os

import psycopg
import pytest


@pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="DATABASE_URL is not set")
def test_database_roundtrip() -> None:
    with psycopg.connect(os.environ["DATABASE_URL"]) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone() == (1,)
