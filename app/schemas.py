from pydantic import BaseModel, HttpUrl
from datetime import datetime


class LinkCreate(BaseModel):
    original_url: HttpUrl


class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: datetime
    clicks: int

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    database: str
