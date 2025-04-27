import redis
import os
import json

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0, decode_responses=True)

def create_job(job_type):
    import uuid
    job_id = str(uuid.uuid4())
    job = {"id": job_id, "status": "queued", "type": job_type}
    r.hset("jobs", job_id, json.dumps(job))
    r.lpush("hot_queue", job_id)
    return job_id

def get_job(job_id):
    job = r.hget("jobs", job_id)
    if job:
        return json.loads(job)
    return None

def set_job_status(job_id, status):
    job = get_job(job_id)
    if job:
        job["status"] = status
        r.hset("jobs", job_id, json.dumps(job))
        return True
    return False

def job_result_ready(job_id):
    return r.hexists("results", job_id)


