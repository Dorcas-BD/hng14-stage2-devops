# hng14-stage2-devops
# Job Processing System — Stage 2 DevOps

A containerized multi-service job processing application built for HNG14 Stage 2.

The system consists of four services:
- **Frontend** (Node.js/Express) — job submission UI and status polling
- **API** (Python/FastAPI) — creates jobs and serves status updates
- **Worker** (Python) — picks up and processes jobs from the queue
- **Redis** — shared message queue and job state store

---

## Prerequisites

Make sure these are installed on your machine before you begin:

- [Docker](https://docs.docker.com/get-docker/) (v24 or newer)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.20 or newer — comes with Docker Desktop)
- Git

Verify your versions:

```bash
docker --version
docker compose version
git --version
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Dorcas-BD/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Set up your environment file

```bash
cp .env.example .env
```

Open `.env` and set a strong Redis password:

```
REDIS_PASSWORD=pick_a_strong_password_here
FRONTEND_PORT=3000
APP_ENV=production
```

> **Important:** Never commit `.env` to git. It is already in `.gitignore`.

### 3. Build and start the full stack

```bash
docker compose up --build
```

To run in the background:

```bash
docker compose up --build -d
```

---

## What a Successful Startup Looks Like

After running `docker compose up --build`, you should see output like:

```
[+] Running 4/4
 ✔ Container redis       Healthy
 ✔ Container api         Healthy
 ✔ Container worker      Started
 ✔ Container frontend    Healthy
```

Services start in dependency order:
1. Redis starts and passes its health check
2. API and worker start (both depend on Redis being healthy)
3. Frontend starts after the API is confirmed healthy

Open your browser at: **http://localhost:3000**

You should see the Job Processor Dashboard. Click **Submit New Job** — the job should appear in the list and change from `queued` → `processing` → `completed` within a few seconds.

---

## Running Tests Locally

### Unit tests (API)

```bash
cd api
pip install -r requirements.txt
pip install pytest pytest-cov httpx
pytest tests/ -v --cov=. --cov-report=term
```

Expected output:

```
tests/test_api.py::test_create_job_returns_job_id PASSED
tests/test_api.py::test_get_existing_job_returns_status PASSED
tests/test_api.py::test_get_nonexistent_job_returns_404 PASSED
3 passed in 0.XXs
```

---

## Stopping the Stack

```bash
docker compose down
```

To also remove the Redis data volume:

```bash
docker compose down -v
```

---

## Project Structure

```
.
├── api/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Pinned Python dependencies
│   ├── Dockerfile           # Multi-stage production image
│   └── tests/
│       └── test_api.py      # Unit tests (Redis mocked)
├── worker/
│   ├── worker.py            # Job processing loop
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.js               # Express server
│   ├── package.json
│   ├── Dockerfile
│   └── public/
│       └── index.html       # Job dashboard UI
├── .github/
│   └── workflows/
│       └── pipeline.yml     # CI/CD pipeline (6 stages)
├── docker-compose.yml
├── .env.example             # Template — copy to .env
├── .gitignore
├── FIXES.md                 # All bugs found and fixed
└── README.md
```

---

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push and executes these stages in strict order:

| Stage | What it does |
|-------|-------------|
| **lint** | flake8 (Python), eslint (JS), hadolint (Dockerfiles) |
| **test** | pytest with Redis mocked, uploads coverage report |
| **build** | Builds all 3 images, tags with git SHA + latest, pushes to local registry |
| **security-scan** | Trivy scans all images, fails on CRITICAL findings, uploads SARIF |
| **integration-test** | Brings full stack up, submits a job, polls until completed, tears down |
| **deploy** | Runs on `main` only — rolling update with 60-second health-check gate |

A failure in any stage stops all subsequent stages from running.

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `REDIS_PASSWORD` | Yes | Password for Redis authentication |
| `FRONTEND_PORT` | No | Host port for the frontend (default: 3000) |
| `APP_ENV` | No | Environment name (default: production) |