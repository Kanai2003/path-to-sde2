from fastapi import APIRouter
from app.api.v1.endpoints import url_shortening

api_router = APIRouter()

api_router.include_router(url_shortening.router, prefix="/urls", tags=["urls"])