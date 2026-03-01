# Docker setup guide

```bash
# Start all services (app + PostgreSQL + Redis)
docker compose up

# Or run in background
docker compose up -d

# View logs
docker compose logs -f app

```

Hot-reload works because:

- `./app` is mounted as a volume → your local changes sync instantly
- uvicorn runs with `--reload` flag → detects changes and restarts

## Production build

```bash
# Build production image
docker build --target production -t url-shortener:prod .

# Run standalone (needs external DB/Redis)
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+psycopg://... \
  -e REDIS_URL=redis://... \
  url-shortener:prod
```

## Run DB Migrations

```bash
# After starting containers
docker compose exec app alembic upgrade head
```
