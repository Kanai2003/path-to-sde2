from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import decode_token
from app.models.user import User
from app.repositories.url_repository import url_repository
from app.repositories.user_repository import user_repository
from app.schemas.url import URLCreate
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import get_auth_service
from app.services.url_shortening_service import get_url_shortening_service

router = APIRouter(tags=["web"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"


def _set_auth_cookies(
    response: RedirectResponse,
    *,
    access_token: str,
    refresh_token: str,
    access_ttl: int,
    refresh_ttl: int,
    secure: bool,
) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=access_ttl,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=refresh_ttl,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )


def _clear_auth_cookies(response: RedirectResponse) -> None:
    response.delete_cookie(key=ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/")


async def _get_current_user_from_cookie(request: Request, db: AsyncSession) -> User | None:
    token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not token:
        return None

    try:
        payload = decode_token(token, expected_type="access")
    except InvalidTokenError:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = await user_repository.get_by_id(db, str(user_id))
    if not user or not user.is_active:
        return None

    return user


async def _recent_urls_context(
    request: Request, db: AsyncSession, user: User | None
) -> list[dict[str, Any]]:
    if not user:
        return []

    base_url = str(request.base_url).rstrip("/")
    urls = await url_repository.list_recent_by_user(db, user.id, limit=20)
    return [
        {
            "short_code": url.short_code,
            "short_url": f"{base_url}/{url.short_code}",
            "original_url": url.original_url,
            "fetch_count": url.fetch_count,
            "created_at": url.created_at,
        }
        for url in urls
    ]


def _redirect_to(path: str, status_code: int = status.HTTP_303_SEE_OTHER) -> RedirectResponse:
    return RedirectResponse(url=path, status_code=status_code)


@router.get("/", response_class=HTMLResponse)
async def web_root() -> Response:
    return _redirect_to("/app")


@router.get("/app", response_class=HTMLResponse)
async def app_home(request: Request, db: AsyncSession = Depends(get_db)) -> Response:
    user = await _get_current_user_from_cookie(request, db)
    recent_urls = await _recent_urls_context(request, db, user)
    return templates.TemplateResponse(
        request=request,
        name="web/home.html",
        context={
            "user": user,
            "recent_urls": recent_urls,
            "short_url": None,
            "error": None,
            "active_page": "home",
        },
    )


@router.post("/app/shorten", response_class=HTMLResponse)
async def shorten_via_web(
    request: Request,
    original_url: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> Response:
    user = await _get_current_user_from_cookie(request, db)
    service = get_url_shortening_service(db)

    short_url = None
    error = None

    if not original_url.strip():
        error = "Please provide a valid URL"
    else:
        try:
            validated = URLCreate(original_url=original_url.strip())
            created = await service.create_short_url(
                str(validated.original_url), user_id=user.id if user else None
            )
            short_url = f"{request.base_url}{created.short_code}".rstrip("/")
        except ValidationError:
            error = "Please provide a valid HTTP/HTTPS URL"
        except Exception:
            error = "Unable to shorten this URL right now. Please try again."

    recent_urls = await _recent_urls_context(request, db, user)
    return templates.TemplateResponse(
        request=request,
        name="web/home.html",
        context={
            "user": user,
            "recent_urls": recent_urls,
            "short_url": short_url,
            "error": error,
            "active_page": "home",
        },
    )


@router.get("/app/login", response_class=HTMLResponse)
async def login_page(request: Request, db: AsyncSession = Depends(get_db)) -> Response:
    user = await _get_current_user_from_cookie(request, db)
    if user:
        return _redirect_to("/app/dashboard")

    return templates.TemplateResponse(
        request=request,
        name="web/login.html",
        context={"error": None, "active_page": "login"},
    )


@router.post("/app/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> Response:
    service = get_auth_service(db)

    try:
        payload = UserLogin(email=email, password=password)
    except ValidationError:
        return templates.TemplateResponse(
            request=request,
            name="web/login.html",
            context={"error": "Please enter a valid email and password.", "active_page": "login"},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    tokens = await service.login(payload)
    if not tokens:
        return templates.TemplateResponse(
            request=request,
            name="web/login.html",
            context={"error": "Invalid email or password.", "active_page": "login"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    response = _redirect_to("/app/dashboard")
    _set_auth_cookies(
        response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        access_ttl=tokens.expires_in,
        refresh_ttl=tokens.refresh_expires_in,
        secure=request.url.scheme == "https",
    )
    return response


@router.get("/app/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    user = await _get_current_user_from_cookie(request, db)
    if user:
        return _redirect_to("/app/dashboard")

    return templates.TemplateResponse(
        request=request,
        name="web/register.html",
        context={"error": None, "active_page": "register"},
    )


@router.post("/app/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> Response:
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="web/register.html",
            context={"error": "Password and confirm password must match.", "active_page": "register"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    service = get_auth_service(db)

    try:
        user_create = UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
    except ValidationError:
        return templates.TemplateResponse(
            request=request,
            name="web/register.html",
            context={"error": "Please provide valid registration details.", "active_page": "register"},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    created = await service.register(user_create)
    if not created:
        return templates.TemplateResponse(
            request=request,
            name="web/register.html",
            context={"error": "An account with this email already exists.", "active_page": "register"},
            status_code=status.HTTP_409_CONFLICT,
        )

    tokens = await service.login(UserLogin(email=email, password=password))
    if not tokens:
        return templates.TemplateResponse(
            request=request,
            name="web/login.html",
            context={"error": "Account created. Please login.", "active_page": "login"},
        )

    response = _redirect_to("/app/dashboard")
    _set_auth_cookies(
        response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        access_ttl=tokens.expires_in,
        refresh_ttl=tokens.refresh_expires_in,
        secure=request.url.scheme == "https",
    )
    return response


@router.get("/app/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: AsyncSession = Depends(get_db)) -> Response:
    user = await _get_current_user_from_cookie(request, db)
    if not user:
        return _redirect_to("/app/login")

    recent_urls = await _recent_urls_context(request, db, user)
    return templates.TemplateResponse(
        request=request,
        name="web/dashboard.html",
        context={"user": user, "recent_urls": recent_urls, "active_page": "dashboard"},
    )


@router.post("/app/logout")
async def logout_submit(request: Request, db: AsyncSession = Depends(get_db)) -> Response:
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    service = get_auth_service(db)

    if refresh_token:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user_id = payload.get("sub")
            if user_id:
                await service.logout(str(user_id), refresh_token)
        except InvalidTokenError:
            pass

    response = _redirect_to("/app")
    _clear_auth_cookies(response)
    return response
