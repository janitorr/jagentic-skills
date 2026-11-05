CREATE TABLE customers (
    id          TEXT PRIMARY KEY,
    tenant_id   TEXT NOT NULL,
    name        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE invoices (
    id          TEXT PRIMARY KEY,
    tenant_id   TEXT NOT NULL,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    status      TEXT NOT NULL CHECK (status IN ('draft', 'open', 'paid', 'void')),
    currency    TEXT NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE invoice_lines (
    id              TEXT PRIMARY KEY,
    invoice_id      TEXT NOT NULL REFERENCES invoices(id),
    description     TEXT NOT NULL,
    quantity        INTEGER NOT NULL,
    unit_amount_cents INTEGER NOT NULL,
    position        INTEGER NOT NULL
);

CREATE TABLE payments (
    id                  TEXT PRIMARY KEY,
    tenant_id           TEXT NOT NULL,
    invoice_id          TEXT NOT NULL REFERENCES invoices(id),
    amount_cents        INTEGER NOT NULL,
    currency            TEXT NOT NULL,
    status              TEXT NOT NULL CHECK (status IN ('pending', 'succeeded', 'failed', 'unknown')),
    provider_charge_id  TEXT,
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL
);
