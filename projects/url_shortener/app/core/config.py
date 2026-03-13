from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    BASE_URL: str = "http://localhost:8000"

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
        """Convert sync URL to async URL for asyncpg."""
        return self.DATABASE_URL.replace(
            "postgresql+psycopg://", "postgresql+asyncpg://"
        ).replace("postgresql://", "postgresql+asyncpg://")


settings = Settings()
