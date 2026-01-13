from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime, date
from typing import Optional, Dict, Any


class LinkCreateRequest(BaseModel):
    target_url: HttpUrl
    campaign: Optional[str] = None
    label: Optional[str] = None
    source: Optional[str] = None
    created_by: Optional[str] = None

    @field_validator('target_url')
    @classmethod
    def validate_target_url(cls, v):
        if not v:
            raise ValueError('target_url cannot be empty')
        url_str = str(v)
        if not (url_str.startswith('http://') or url_str.startswith('https://')):
            raise ValueError('target_url must be http or https')
        return v


class LinkCreateResponse(BaseModel):
    id: int
    slug: str
    short_url: str
    target_url: str
    created_at: datetime
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class LinkResponse(BaseModel):
    id: int
    slug: str
    target_url: str
    created_at: datetime
    created_by: Optional[str] = None
    campaign: Optional[str] = None
    label: Optional[str] = None
    source: Optional[str] = None
    is_disabled: bool

    class Config:
        from_attributes = True


class LinkClickCreate(BaseModel):
    link_id: int
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_hash: str
    ip_truncated_or_null: Optional[str] = None
    day: date


class LinkClickResponse(BaseModel):
    id: int
    link_id: int
    clicked_at: datetime
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_hash: str
    ip_truncated_or_null: Optional[str] = None
    day: date

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    database: str
