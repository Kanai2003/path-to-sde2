"""URL shortening endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.url import URLCreate, URLResponse
from app.services.url_shortening_service import get_url_shortening_service
from app.api.deps import get_db
from app.core.exceptions import ShortCodeGenerationError

router = APIRouter()


@router.post(
    "/",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create shortened URL",
    response_description="The created shortened URL"
)
def create_url(
    data: URLCreate,
    db: Session = Depends(get_db)
) -> URLResponse:
    """
    Create a shortened URL from the original URL.

    - **original_url**: A valid HTTP/HTTPS URL to shorten
    """
    service = get_url_shortening_service(db)

    try:
        url = service.create_short_url(str(data.original_url))
        return URLResponse.model_validate(url)
    except ShortCodeGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
