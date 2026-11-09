"""1.4: check that Python can reach Postgres."""

import os

import psycopg

DEFAULT_DSN = "postgresql://postgres:postgres@localhost:5432/postgres"
DSN = os.environ.get("DATABASE_URL", DEFAULT_DSN)

with psycopg.connect(DSN) as conn:
    version = conn.execute("SELECT version();").fetchone()[0]

print(version)
