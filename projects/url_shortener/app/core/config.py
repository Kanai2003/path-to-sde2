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
    
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB_CACHE: int = 0  # For caching URL mappings
    REDIS_DB_ANALYTICS: int = 1 # For analytics data
    REDIS_DB_QUEUE: int = 2 # For message queue
    


settings = Settings()
