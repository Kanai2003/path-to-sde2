from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints.url_redirect import router as redirect_router
from app.api.v1.router import api_router
from app.core.cache import init_caches
from app.core.config import settings
from app.core.message_queue import init_queue
from app.core.rate_limiter import setup_rate_limiter
from app.core.redis_pool import redis_pool_manager
from app.core.scheduler import analytics_scheduler
from app.utils.logger import logger
from app.web.router import router as web_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Startup:
    - Initialize Redis connection pools
    - Initialize cache instances
    - Initialize message queue
    - Start analytics scheduler
    
    Shutdown:
    - Stop scheduler
    - Close Redis connection pools
    """
    # === STARTUP ===
    logger.info("Starting application...")
    
    # Initialize Redis connection pools first
    await redis_pool_manager.init_pools()
    logger.info("Redis pools initialized")
    
    # Initialize caches (uses Redis pools)
    init_caches()
    logger.info("Cache instances initialized")
    
    # Initialize message queue (uses Redis pools)
    init_queue()
    logger.info("Message queue initialized")
    
    # Start analytics scheduler
    analytics_scheduler.start()
    logger.info("Analytics scheduler started")
    
    yield  # Application runs here
    
    # === SHUTDOWN ===
    logger.info("Shutting down application...")
    
    # Stop scheduler first
    analytics_scheduler.stop()
    
    # Close Redis pools
    await redis_pool_manager.close_pools()
    logger.info("Redis pools closed")


app = FastAPI(
    title="URL Shortener",
    description="High-performance URL shortening service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Setup rate limiter (conditionally enabled based on settings)
setup_rate_limiter(app)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Server-rendered web routes
app.include_router(web_router)

# Versioned API routes
app.include_router(api_router, prefix="/api/v1")

# Root-level redirect (must be LAST to avoid conflicts with API routes)
app.include_router(redirect_router, tags=["Redirect"])
