from pydantic import BaseModel, HttpUrl, computed_field
from app.core.config import settings

class URLBase(BaseModel):
    original_url: HttpUrl

class URLCreate(URLBase):
    pass
    
class URLResponse(URLBase):
    short_code: str

    @computed_field
    @property
    def short_url(self) -> str:
        return f"{settings.BASE_URL}/{self.short_code}"

    model_config = {"from_attributes": True}
