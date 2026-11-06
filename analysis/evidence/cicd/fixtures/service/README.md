# orders-api

FastAPI service for order lookup. Python 3.12, uvicorn, Postgres.

## Commands

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt

ruff check .
mypy src
pytest
docker build -t orders-api .
```

The integration tests need `DATABASE_URL` and skip when it is unset.
