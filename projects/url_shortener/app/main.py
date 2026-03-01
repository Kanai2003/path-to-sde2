from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.v1.router import api_router
from app.api.v1.endpoints.url_redirect import router as redirect_router
from app.core.config import settings
from app.core.rate_limiter import setup_rate_limiter
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

# Setup rate limiter (conditionally enabled based on settings)
setup_rate_limiter(app)

# Load HTML template
TEMPLATES_DIR = Path(__file__).parent / "templates"


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the URL shortener homepage."""
    html_content = (TEMPLATES_DIR / "index.html").read_text()
    return HTMLResponse(content=html_content)


# Versioned API routes
app.include_router(api_router, prefix="/api/v1")

# Root-level redirect (must be LAST to avoid conflicts with API routes)
app.include_router(redirect_router, tags=["Redirect"])