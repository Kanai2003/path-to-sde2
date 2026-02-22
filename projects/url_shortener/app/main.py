from fastapi import FastAPI
from app.api.v1.router import api_router
from app.api.v1.endpoints.url_redirect import router as redirect_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="URL Shortener", 
    description="URL shortening service", 
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the URL Shortener API!"}


# Versioned API routes
app.include_router(api_router, prefix="/api/v1")

# Root-level redirect (must be LAST to avoid conflicts with API routes)
app.include_router(redirect_router, tags=["Redirect"])