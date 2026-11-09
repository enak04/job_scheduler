"""Database settings shared by the API and the worker."""

import os

DEFAULT_DSN = "postgresql://postgres:postgres@localhost:5432/postgres"
DSN = os.environ.get("DATABASE_URL", DEFAULT_DSN)
