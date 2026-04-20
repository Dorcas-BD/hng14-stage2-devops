import redis
import sys
import time
import os
import signal

redis_host = os.getenv("REDIS_HOST", "redis")
redis_password = os.getenv("REDIS_PASSWORD", None)

r = redis.Redis(host=redis_host, port=6379, password=redis_password)

shutdown = False


def handle_sigterm(signum, frame):
    global shutdown
    print("Received SIGTERM, finishing current job then shutting down...")
    shutdown = True


signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)


def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


while not shutdown:
    job = r.brpop("jobs", timeout=5)
    if job:
        _, job_id = job
        process_job(job_id.decode())

print("Worker shut down cleanly.")
sys.exit(0)