from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.schemas import LinkCreateRequest, LinkCreateResponse, LinkListResponse, LinkResponse
from app.models import Link
from app.utils import generate_unique_slug
from app.config import settings

router = APIRouter(prefix="/links", tags=["links"])

@router.post("", response_model=LinkCreateResponse, status_code=status.HTTP_201_CREATED)
def create_link(request: LinkCreateRequest, db: Session = Depends(get_db)):
    try:
        slug = generate_unique_slug(db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate unique slug"
        )

    new_link = Link(
        slug=slug,
        target_url=str(request.target_url),
        extra=request.extra,
        is_disabled=False
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    short_url = f"{settings.BASE_DOMAIN}/{new_link.slug}"

    return LinkCreateResponse(
        id=new_link.id,
        slug=new_link.slug,
        short_url=short_url,
        target_url=new_link.target_url,
        created_at=new_link.created_at,
        extra=new_link.extra
    )

@router.get("", response_model=LinkListResponse)
def list_links(query: Optional[str] = Query(None), db: Session = Depends(get_db)):
    links_query = db.query(Link)

    if query:
        search_pattern = f"%{query}%"
        links_query = links_query.filter(
            (Link.slug.ilike(search_pattern)) |
            (Link.target_url.ilike(search_pattern)) |
            (Link.extra.ilike(search_pattern))
        )

    links = links_query.order_by(Link.created_at.desc()).all()

    return LinkListResponse(
        links=[LinkResponse.model_validate(link) for link in links],
        total=len(links)
    )
