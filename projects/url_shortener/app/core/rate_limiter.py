"""Rate limiting configuration using slowapi."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.core.config import settings


def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key based on client IP."""
    if not settings.RATE_LIMIT_ENABLED:
        return ""  # Return empty string to bypass rate limiting
    return get_remote_address(request)


# Initialize limiter with conditional storage
if settings.RATE_LIMIT_ENABLED:
    limiter = Limiter(
        key_func=get_rate_limit_key,
        storage_uri=settings.REDIS_URL,
        strategy="fixed-window"
    )
else:
    # Use in-memory storage when disabled (won't actually limit)
    limiter = Limiter(
        key_func=get_rate_limit_key,
        storage_uri="memory://",
        strategy="fixed-window"
    )


def get_rate_limit_string() -> str:
    """Get rate limit string based on settings."""
    return f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW}"


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "message": f"Too many requests. Please try again later.",
            "retry_after": exc.detail
        }
    )


def setup_rate_limiter(app: FastAPI) -> None:
    """Setup rate limiter middleware and exception handler."""
    if settings.RATE_LIMIT_ENABLED:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)


# Conditional rate limit decorator
def conditional_rate_limit():
    """
    Returns a rate limit decorator if rate limiting is enabled,
    otherwise returns a no-op decorator.
    """
    if settings.RATE_LIMIT_ENABLED:
        return limiter.limit(get_rate_limit_string())
    else:
        # No-op decorator when rate limiting is disabled
        def no_op_decorator(func):
            return func
        return no_op_decorator
