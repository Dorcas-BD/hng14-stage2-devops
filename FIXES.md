# FIXES.md

Every bug found in the starter repository, documented with file, line, problem, and fix.

---

## Fix 1 — Hardcoded Redis host in API

- **File:** `api/main.py`
- **Line:** 8
- **Problem:** `redis.Redis(host="localhost")` — hardcoded to localhost. Inside Docker, each service runs in its own container. `localhost` inside the API container refers to that container only, not the Redis container. The connection will always fail.
- **Fix:** Changed to `redis.Redis(host=os.getenv("REDIS_HOST", "redis"))` so the host is read from an environment variable, defaulting to `"redis"` (the Docker Compose service name).

---

## Fix 2 — Redis password not used in API

- **File:** `api/main.py`
- **Line:** 8
- **Problem:** The `.env` file sets `REDIS_PASSWORD` but the API never reads or passes it to the Redis client. If Redis is started with `--requirepass`, every command will return an `AUTHENTICATIONERROR`.
- **Fix:** Added `password=os.getenv("REDIS_PASSWORD", None)` to the `redis.Redis(...)` call.

---

## Fix 3 — `get_job` returns HTTP 200 for a missing job

- **File:** `api/main.py`
- **Line:** 16–18
- **Problem:** When a job is not found, the handler returns `{"error": "not found"}` with status code 200. This breaks any client that checks the HTTP status code to detect errors, and it breaks the integration test which expects a proper 404.
- **Fix:** Replaced the manual dict return with `raise HTTPException(status_code=404, detail="Job not found")`.

---

## Fix 4 — No `/health` endpoint on the API

- **File:** `api/main.py`
- **Line:** (missing)
- **Problem:** Docker's `HEALTHCHECK` and `depends_on: condition: service_healthy` both require an endpoint to probe. Without one, the health check fails and dependent services never start.
- **Fix:** Added `GET /health` that calls `r.ping()` and returns `{"status": "ok"}`.

---

## Fix 5 — Hardcoded Redis host in worker

- **File:** `worker/worker.py`
- **Line:** 5
- **Problem:** Same issue as Fix 1 — `redis.Redis(host="localhost")` fails inside Docker.
- **Fix:** Changed to `redis.Redis(host=os.getenv("REDIS_HOST", "redis"))`.

---

## Fix 6 — Redis password not used in worker

- **File:** `worker/worker.py`
- **Line:** 5
- **Problem:** Same as Fix 2 — `REDIS_PASSWORD` is never passed to the Redis client in the worker.
- **Fix:** Added `password=os.getenv("REDIS_PASSWORD", None)`.

---

## Fix 7 — `signal` imported but graceful shutdown never implemented

- **File:** `worker/worker.py`
- **Line:** 4 (import), missing implementation
- **Problem:** `import signal` appears in the original but no signal handlers are registered. When Docker stops a container it sends `SIGTERM`. Without a handler, the Python process is killed immediately — potentially mid-job, leaving jobs stuck in a `queued` state forever with no worker to pick them up.
- **Fix:** Added `handle_sigterm()` registered on both `SIGTERM` and `SIGINT`. The loop checks a `shutdown` flag so the current job finishes before the process exits cleanly.

---

## Fix 8 — Queue name mismatch between API and worker

- **File:** `api/main.py` line 11, `worker/worker.py` line 18
- **Problem:** API pushes to queue named `"job"` (singular); worker pops from `"job"` too — in this specific code they accidentally match. However the consistent, documented name should be `"jobs"` (plural) to follow Redis key naming conventions and avoid confusion when inspecting the queue manually.
- **Fix:** Renamed both to `"jobs"` for consistency and clarity.

---

## Fix 9 — Hardcoded `API_URL` in frontend

- **File:** `frontend/app.js`
- **Line:** 5
- **Problem:** `const API_URL = "http://localhost:8000"` — same container networking issue. Inside Docker, the frontend container cannot reach the API container via localhost.
- **Fix:** Changed to `const API_URL = process.env.API_URL || "http://api:8000"` so it reads from an environment variable set in `docker-compose.yml`.

---

## Fix 10 — `index.html` in wrong directory

- **File:** `frontend/app.js` line 8, `frontend/index.html` location
- **Problem:** `app.js` serves static files from `path.join(__dirname, 'views')` but `index.html` is at the project root. The file would never be served — every request for `/` would return a 404.
- **Fix:** Changed static path to `'public'` and moved `index.html` into `frontend/public/index.html`.

---

## Fix 11 — Unpinned Python dependencies in API

- **File:** `api/requirements.txt`
- **Lines:** 1–3
- **Problem:** `fastapi`, `uvicorn`, `redis` have no version pins. A future `pip install` could pull in a breaking release and the build would silently break with no code change.
- **Fix:** Pinned to `fastapi==0.111.0`, `uvicorn[standard]==0.29.0`, `redis==5.0.4`.

---

## Fix 12 — Unpinned Python dependency in worker

- **File:** `worker/requirements.txt`
- **Line:** 1
- **Problem:** `redis` unpinned.
- **Fix:** Pinned to `redis==5.0.4` to match the API.

---

## Fix 13 — `.env` file with real secrets committed (critical)

- **File:** `.env` (root)
- **Problem:** The starter repo shipped with a real `.env` file containing `REDIS_PASSWORD=supersecretpassword123`. Committing secrets to git — even once — means they are permanently in the git history and must be treated as compromised.
- **Fix:** Added `.env` to `.gitignore`. Created `.env.example` with placeholder values for all required variables. The actual `.env` is never committed.

---

## Fix 14 — No `engines` field in package.json

- **File:** `frontend/package.json`
- **Problem:** No Node.js version constraint. Running on an unexpected Node version (e.g., Node 14) could cause subtle incompatibilities with the Express/Axios versions used.
- **Fix:** Added `"engines": { "node": ">=18.0.0" }`.