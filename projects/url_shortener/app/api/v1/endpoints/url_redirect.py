"""URL redirection endpoint."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.services.url_redirection_service import get_url_redirection_service
from app.api.deps import get_db
from app.core.exceptions import URLNotFoundError
from app.core.rate_limiter import limiter, get_rate_limit_string
from app.core.config import settings

router = APIRouter()


@router.get(
    "/{short_code}",
    summary="Redirect to original URL",
    response_class=RedirectResponse,
    responses={
        302: {"description": "Redirect to original URL"},
        404: {"description": "Short code not found"}
    }
)
@limiter.limit(get_rate_limit_string(), exempt_when=lambda: not settings.RATE_LIMIT_ENABLED)
def redirect_url(
    request: Request,
    short_code: str,
    db: Session = Depends(get_db)
) -> RedirectResponse:
    """Redirect short code to original URL."""
    service = get_url_redirection_service(db)

    try:
        original_url = service.get_original_url(short_code)
        return RedirectResponse(url=original_url, status_code=status.HTTP_302_FOUND)
    except URLNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found"
        )
