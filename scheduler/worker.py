"""Runs jobs from the jobs table. Start with: python -m scheduler.worker"""

import os
import socket
import time

import psycopg

from scheduler.db import DSN
from scheduler.handlers import get_handler

POLL_INTERVAL_SECONDS = 1


def pick_next_job(conn):
    """Return (id, job_type, payload) for the most urgent runnable job, or None."""
    return conn.execute(
        """
        SELECT id, job_type, payload
        FROM jobs
        WHERE status = 'PENDING'
          AND run_at <= now()
        ORDER BY priority DESC, run_at ASC
        LIMIT 1
        """
    ).fetchone()


def claim_job(conn, job_id):
    """Mark a job RUNNING. Returns False if it is no longer PENDING."""
    cur = conn.execute(
        """
        UPDATE jobs
        SET status = 'RUNNING',
            attempts = attempts + 1,
            updated_at = now()
        WHERE id = %s
          AND status = 'PENDING'
        """,
        (job_id,),
    )
    return cur.rowcount == 1


def finish_job(conn, job_id):
    """Mark a job SUCCEEDED. Returns False if it is no longer RUNNING."""
    cur = conn.execute(
        """
        UPDATE jobs
        SET status = 'SUCCEEDED',
            updated_at = now()
        WHERE id = %s
          AND status = 'RUNNING'
        """,
        (job_id,),
    )
    return cur.rowcount == 1


def run_once(conn, worker_id):
    """Try to run one job. Returns False if there was nothing to pick."""
    job = pick_next_job(conn)
    if job is None:
        return False

    job_id, job_type, payload = job

    if not claim_job(conn, job_id):
        print(f"[{worker_id}] job {job_id}: another worker claimed it first")
        return True

    print(f"[{worker_id}] job {job_id}: running {job_type}")
    try:
        handler = get_handler(job_type)
        handler(payload)
    except Exception as exc:
        # For now the error is only logged, so the job stays RUNNING.
        # Milestone 4 turns this into a retry or DEAD.
        print(f"[{worker_id}] job {job_id}: failed: {exc!r}")
        return True

    if finish_job(conn, job_id):
        print(f"[{worker_id}] job {job_id}: succeeded")
    else:
        print(f"[{worker_id}] job {job_id}: could not be marked finished")
    return True


def main():
    worker_id = f"{socket.gethostname()}-{os.getpid()}"
    # autocommit: each statement is saved immediately, so other connections
    # see RUNNING while the job is still being worked on.
    with psycopg.connect(DSN, autocommit=True) as conn:
        print(f"[{worker_id}] worker started")
        try:
            while True:
                if not run_once(conn, worker_id):
                    time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print(f"[{worker_id}] worker stopped")


if __name__ == "__main__":
    main()
