import pytest
import uuid
from jobs import create_job, get_job, set_job_status, job_result_ready
import redis
import os

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0, decode_responses=True)

def test_create_and_get_job():
    job_type = "timeline"
    job_id = create_job(job_type)
    job = get_job(job_id)
    assert job is not None
    assert job["id"] == job_id
    assert job["type"] == job_type
    assert job["status"] == "queued"

def test_set_job_status():
    job_id = create_job("sector")
    set_job_status(job_id, "running")
    job = get_job(job_id)
    assert job["status"] == "running"

def test_job_result_ready():
    job_id = create_job("geography")
    # No result yet
    assert not job_result_ready(job_id)
    # Simulate result
    r.hset("results", job_id, b"testimage")
    assert job_result_ready(job_id)
    r.hdel("results", job_id)

