# Docker Setup Guide

## Services

| Service            | Description                            | Port        |
| ------------------ | -------------------------------------- | ----------- |
| `app`              | FastAPI app (4 Uvicorn workers)        | `8000`      |
| `analytics-worker` | Redis Stream consumer, batch DB writes | —           |
| `db`               | PostgreSQL 16                          | `5433→5432` |
| `redis`            | Redis (cache + queue)                  | `6379`      |

---

## Starting the Stack

```bash
# Build images and start all services
docker compose up --build

# Start in background (detached)
docker compose up --build -d

# Stop all services
docker compose down

# Stop and remove volumes (wipes the database)
docker compose down -v
```

---

## Database Migrations

Run after the stack is up for the first time, or after adding new migrations:

```bash
docker compose exec app alembic upgrade head
```

---

## Viewing Logs

### All services at once

```bash
docker compose logs -f
```

### Single service

```bash
docker compose logs -f app
docker compose logs -f analytics-worker
docker compose logs -f db
docker compose logs -f redis
```

### Last N lines

```bash
docker compose logs --tail=100 app
docker compose logs --tail=50 analytics-worker
```

### Since a specific time

```bash
docker compose logs --since=10m app        # last 10 minutes
docker compose logs --since=1h app         # last 1 hour
docker compose logs --since="2026-03-13T00:00:00" app
```

### Filter log output

```bash
# Show only errors and warnings
docker compose logs -f app | grep -E "ERROR|WARNING"

# Show startup/shutdown events
docker compose logs app | grep -E "startup|shutdown|lifespan"

# Show analytics worker batch flush events
docker compose logs -f analytics-worker | grep "Flushed"
```

### Raw container logs (via docker directly)

```bash
# List container names first
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Then tail a specific container
docker logs -f url_shortener-app-1
docker logs -f url_shortener-analytics-worker-1
docker logs --tail=200 url_shortener-app-1
```

---

## Rebuilding

After code changes, rebuild the affected service:

```bash
# Rebuild a single service
docker compose build app
docker compose build analytics-worker

# Rebuild without cache (use when dependencies change)
docker compose build --no-cache app
docker compose build --no-cache analytics-worker

# Rebuild all and restart
docker compose up --build -d
```

---

## Port Conflicts

If port `5433` is already in use:

```bash
# Find what's holding the port
ss -ltnp | grep ':5433'

# Stop a running compose stack
docker compose down

# Or change the host port in docker-compose.yml
# ports: "5434:5432"  ← use a free port
```

---

## Health Check

```bash
# App liveness
curl -s http://localhost:8000/health

# Shorten a URL (quick smoke test)
curl -s -X POST http://localhost:8000/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com"}'
```
