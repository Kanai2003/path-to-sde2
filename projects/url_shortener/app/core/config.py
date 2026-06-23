from pydantic_settings import BaseSettings, SettingsConfigDict

# Accepted Postgres URL schemes, longest-prefix first so the more specific
# driver-qualified schemes match before the bare ones.
_PG_SCHEMES = (
    "postgresql+asyncpg://",
    "postgresql+psycopg://",
    "postgresql+psycopg2://",
    "postgresql://",
    "postgres://",  # Railway / Heroku style
)


def _with_driver(url: str, driver_scheme: str) -> str:
    """Rewrite any supported Postgres URL to use the given driver scheme.

    Railway/Heroku hand out URLs like ``postgresql://...`` (or legacy
    ``postgres://...``) with no driver. SQLAlchemy then defaults to psycopg2,
    which is not installed. We normalize to an explicit driver instead.
    """
    for scheme in _PG_SCHEMES:
        if url.startswith(scheme):
            return driver_scheme + url[len(scheme) :]
    return url


class Settings(BaseSettings):
    DATABASE_URL: str
    BASE_URL: str = "http://localhost:8000"
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    CORS_ORIGINS: list[str] = [
        "http://localhost:*",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Rate Limiting Settings
    RATE_LIMIT_ENABLED: bool = False  # Disabled by default for local testing
    RATE_LIMIT_REQUESTS: int = 100  # Number of requests
    RATE_LIMIT_WINDOW: str = "minute"  # Time window: second, minute, hour, day

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB_CACHE: int = 0  # For caching URL mappings
    REDIS_DB_ANALYTICS: int = 1  # For analytics data
    REDIS_DB_QUEUE: int = 2  # For message queue
    REDIS_MAX_CONNECTIONS: int = 100  # Connection pool size

    # Database Pool Settings
    DB_POOL_SIZE: int = 20  # Number of persistent connections
    DB_MAX_OVERFLOW: int = 30  # Extra connections under load
    DB_POOL_RECYCLE: int = 3600  # Recycle connections after 1 hour

    # Worker Settings
    WORKER_BATCH_SIZE: int = 1000  # Events per batch flush
    WORKER_FLUSH_INTERVAL: int = 5  # Seconds between flushes

    @property
    def async_database_url(self) -> str:
        """URL for the async app engine (asyncpg driver)."""
        return _with_driver(self.DATABASE_URL, "postgresql+asyncpg://")

    @property
    def sync_database_url(self) -> str:
        """URL for the sync engine + Alembic migrations (psycopg v3 driver)."""
        return _with_driver(self.DATABASE_URL, "postgresql+psycopg://")


settings = Settings()
