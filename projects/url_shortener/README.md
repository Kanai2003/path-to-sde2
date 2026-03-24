# BitTrail URL Shortener

Production-oriented URL shortener built with FastAPI, PostgreSQL, Redis, JWT auth, and async analytics workers.

It serves both the web UI and API from one backend application.

## Project Overview

BitTrail is designed to keep redirect latency low while still collecting analytics at scale.

- Fast redirect path with cache + DB fallback
- Async analytics processing via queue + worker
- JWT auth with refresh token rotation
- Account-aware dashboard and recent links
- Optional Redis-backed rate limiting
- Docker-first local and production-like setup

## UI Showcase

### Homepage (Web UI)

![BitTrail Homepage](docs/UI-home-page.png)

Web entrypoints:

- `GET /` -> redirects to `/app`
- `GET /app` -> homepage
- `GET /app/login` -> login page
- `GET /app/register` -> register page
- `GET /app/dashboard` -> user dashboard

## Final Performance Report

### Load Test Snapshot

![Final Performance Report](docs/final_performance.png)

Performance summary from the latest run:

- Total requests: 50,000
- Aggregated average RPS: 1424.56
- Single high-volume mean RPS: 1510.47
- Concurrency tested: 1000
- Target check: passed (`>= 1000 RPS`)

## Throughput Capability

This project is currently capable of approximately **1000 to 1500 RPS** on redirect-heavy workloads, based on the included benchmark runs.

Observed range in this repository:

- Stable target threshold: `1000+ RPS`
- Typical measured zone: `~1425 RPS`
- Peak in shown run: `~1510 RPS`

Latency from the same high-volume run:

- p50: 651ms
- p95: 743ms
- p99: 908ms

Note: actual throughput varies by CPU, Docker context, database state, network, and background traffic.

## Architecture At A Glance

Core request flow:

`Client -> API -> Service -> Repository -> DB`

UI serving flow:

1. Browser hits `/app`
2. FastAPI web router resolves the route
3. Handler prepares user/recent-link context
4. Jinja template renders HTML on server
5. CSS is served from `/static/web.css`

Relevant files:

- App wiring: `app/main.py`
- Web routes: `app/web/router.py`
- Templates: `app/templates/web/*.html`
- Static styles: `app/static/web.css`

### Architecture Visuals

![Layer Architecture Flow](docs/layer-architech-flow.png)

![High Level Design](docs/HLD.png)

## Core Capabilities

- Create short URLs via API and web form
- Redirect using `/{short_code}`
- JWT auth APIs:
  - `/api/v1/auth/register`
  - `/api/v1/auth/login`
  - `/api/v1/auth/refresh`
  - `/api/v1/auth/logout`
  - `/api/v1/auth/logout-all`
  - `/api/v1/auth/me`
- User-linked URL history
- Queue-backed analytics batching
- Optional route-level rate limiting

## Run Guide

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- Optional: Docker + Docker Compose

### Local Run

```bash
cp .env.sample .env

python -m venv .venv
source .venv/bin/activate

pip install -e .
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

- Homepage: `http://localhost:8000/app`
- API docs: `http://localhost:8000/docs`

### Docker Run

```bash
docker compose up --build
```

Detached:

```bash
docker compose up --build -d
```

Stop:

```bash
docker compose down
```

## Benchmark / Load Test Guide

### Apache Bench (recommended for redirect stress test)

```bash
./scripts/ab_load_test.sh
./scripts/ab_load_test.sh -n 50000 -c 1000
```

### Python scripts

```bash
python scripts/load_test.py --url http://localhost:8000 --requests 1000 --concurrent 100
python scripts/redirect_load_test.py --url http://localhost:8000 --requests 50000 --concurrent 1000
```

## Health Check

```bash
curl -s http://localhost:8000/health

curl -s -X POST http://localhost:8000/api/v1/urls/ \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://example.com"}'
```

## Environment Configuration

All environment keys are documented in `.env.sample`.

Includes:

- Core app and database settings
- JWT token settings
- CORS settings
- Rate limiting controls
- Redis DB split and connection pools
- DB pool tuning
- Worker flush and batching settings

