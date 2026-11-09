"""HTTP API for jobs. Start with: uvicorn scheduler.api:app --reload"""

from datetime import datetime
from typing import Any, Optional

import psycopg
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from pydantic import AwareDatetime, BaseModel, Field

from scheduler.db import DSN
from scheduler.handlers import UnknownJobType, get_handler

app = FastAPI(title="Job Scheduler")


class JobCreate(BaseModel):
    job_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0)
    run_at: Optional[AwareDatetime] = None
    max_attempts: int = Field(default=5, ge=1)


class JobCreated(BaseModel):
    id: int


class JobResponse(BaseModel):
    id: int
    status: str
    job_type: str
    payload: dict[str, Any]
    priority: int
    run_at: datetime
    attempts: int
    max_attempts: int
    lease_owner: Optional[str]
    lease_expires_at: Optional[datetime]
    last_error: Optional[str]
    created_at: datetime
    updated_at: datetime


@app.post("/jobs", status_code=201, response_model=JobCreated)
def create_job(job: JobCreate):
    try:
        get_handler(job.job_type)
    except UnknownJobType:
        raise HTTPException(400, f"unknown job_type: {job.job_type}") from None

    with psycopg.connect(DSN) as conn:
        job_id = conn.execute(
            """
            INSERT INTO jobs (job_type, payload, priority, run_at, max_attempts)
            VALUES (%s, %s, %s, COALESCE(%s, now()), %s)
            RETURNING id
            """,
            (
                job.job_type,
                Jsonb(job.payload),
                job.priority,
                job.run_at,
                job.max_attempts,
            ),
        ).fetchone()[0]

    return {"id": job_id}


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int):
    with psycopg.connect(DSN, row_factory=dict_row) as conn:
        job = conn.execute(
            "SELECT * FROM jobs WHERE id = %s",
            (job_id,),
        ).fetchone()

    if job is None:
        raise HTTPException(404, "job not found")
    return job
