from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import url_shortening

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(url_shortening.router, prefix="/urls", tags=["urls"])
