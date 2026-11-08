-- jobs: one row per job. Rebuilt automatically on first startup
-- (mounted into /docker-entrypoint-initdb.d).

CREATE TABLE jobs (
    id BIGSERIAL PRIMARY KEY,

    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'RUNNING', 'SUCCEEDED', 'DEAD')),

    job_type TEXT NOT NULL,

    payload JSONB NOT NULL DEFAULT '{}'::JSONB,

    priority INTEGER NOT NULL DEFAULT 0
        CHECK (priority >= 0),

    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    attempts INTEGER NOT NULL DEFAULT 0
        CHECK (attempts >= 0),

    max_attempts INTEGER NOT NULL DEFAULT 5
        CHECK (max_attempts >= 1),

    lease_owner TEXT,

    lease_expires_at TIMESTAMPTZ,

    last_error TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- a lease is all-or-nothing: owner and expiry are both set or both NULL
    CONSTRAINT lease_pair_check CHECK (
        (lease_owner IS NULL AND lease_expires_at IS NULL)
        OR
        (lease_owner IS NOT NULL AND lease_expires_at IS NOT NULL)
    )
);