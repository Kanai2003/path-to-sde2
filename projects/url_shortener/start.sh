#!/usr/bin/env sh
# Production entrypoint: apply migrations, then start the API.
# - $PORT is injected by Railway; default to 8000 for local/docker use.
# - $WEB_CONCURRENCY controls worker count (keep low on small instances).
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn on port ${PORT:-8000} with ${WEB_CONCURRENCY:-2} worker(s)..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --backlog 2048
