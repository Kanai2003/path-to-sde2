# syntax=docker/dockerfile:1

# =========================================
# Base stage - common dependencies
# =========================================
FROM python:3.13-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./

# =========================================
# Development stage - with hot-reload
# =========================================
FROM base AS development

# Install all dependencies including dev
RUN uv pip install --system -e ".[dev]"

# Copy application code (will be overridden by volume mount in dev)
COPY . .

# Expose port
EXPOSE 8000

# Run with hot-reload enabled
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =========================================
# Production stage - optimized image
# =========================================
FROM base AS production

# Install only production dependencies
RUN uv pip install --system -e .

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose port
EXPOSE 8000

# Run without reload, with multiple workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
