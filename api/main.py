from fastapi import FastAPI,  HTTPException
import redis
import uuid
import os

app = FastAPI()
redis_host = os.getenv("REDIS_HOST", "redis")
redis_password = os.getenv("REDIS_PASSWORD", None)

r = redis.Redis(host=redis_host, port=6379, password=redis_password)

@app.get("/health")
def health():
    """Health check endpoint for Docker HEALTHCHECK and load balancer probes."""
    r.ping()
    return {"status": "ok"}

@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)
    r.hset(f"job:{job_id}", "status", "queued")
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": status.decode()}
