"""1.4: insert a job from Python, then read it back on a new connection."""

import os

import psycopg
from psycopg.types.json import Jsonb

DEFAULT_DSN = "postgresql://postgres:postgres@localhost:5432/postgres"
DSN = os.environ.get("DATABASE_URL", DEFAULT_DSN)

# Leaving this block commits the transaction, or rolls it back on an exception.
with psycopg.connect(DSN) as conn:
    job_id = conn.execute(
        """
        INSERT INTO jobs (job_type, payload, priority)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        ("send_email", Jsonb({"to": "someone@example.com"}), 5),
    ).fetchone()[0]

# A separate connection can only see the row if the insert was committed.
with psycopg.connect(DSN) as conn:
    row = conn.execute(
        "SELECT id, status, job_type, payload, priority FROM jobs WHERE id = %s",
        (job_id,),
    ).fetchone()

print(row)
