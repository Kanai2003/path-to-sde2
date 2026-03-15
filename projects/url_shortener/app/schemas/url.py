from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field

from app.core.config import settings


class URLBase(BaseModel):
    original_url: HttpUrl


class URLCreate(URLBase):
    pass


class URLResponse(URLBase):
    short_code: str = Field(min_length=1, max_length=10)

    @computed_field
    @property
    def short_url(self) -> str:
        return f"{settings.BASE_URL}/{self.short_code}"

    model_config = ConfigDict(from_attributes=True)
