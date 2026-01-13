from fastapi import FastAPI, Depends, status, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, func, distinct
from datetime import datetime, date
from typing import Optional

from app.db import get_db
from app.schemas import (
    HealthResponse, LinkCreateRequest, LinkCreateResponse,
    LinkStatsResponse, LinkBasic, DailyStats, LinkListResponse, LinkResponse
)
from app.models import Link, LinkClick
from app.utils import generate_unique_slug, hash_ip, truncate_ip
from app.config import settings

app = FastAPI(
    title="Linkly",
    description="URL Shortener Service",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status
    }


@app.post("/links", response_model=LinkCreateResponse, status_code=status.HTTP_201_CREATED)
def create_link(request: LinkCreateRequest, db: Session = Depends(get_db)):
    try:
        slug = generate_unique_slug(db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate unique slug"
        )

    new_link = Link(
        slug=slug,
        target_url=str(request.target_url),
        campaign=request.campaign,
        label=request.label,
        source=request.source,
        created_by=request.created_by,
        is_disabled=False
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    short_url = f"https://{settings.BASE_DOMAIN}/{new_link.slug}"

    metadata = {}
    if request.campaign:
        metadata["campaign"] = request.campaign
    if request.label:
        metadata["label"] = request.label
    if request.source:
        metadata["source"] = request.source
    if request.created_by:
        metadata["created_by"] = request.created_by

    return LinkCreateResponse(
        id=new_link.id,
        slug=new_link.slug,
        short_url=short_url,
        target_url=new_link.target_url,
        created_at=new_link.created_at,
        metadata=metadata
    )


@app.get("/links", response_model=LinkListResponse)
def list_links(query: Optional[str] = Query(None), db: Session = Depends(get_db)):
    links_query = db.query(Link)

    if query:
        search_pattern = f"%{query}%"
        links_query = links_query.filter(
            (Link.slug.ilike(search_pattern)) |
            (Link.target_url.ilike(search_pattern)) |
            (Link.campaign.ilike(search_pattern)) |
            (Link.label.ilike(search_pattern)) |
            (Link.source.ilike(search_pattern))
        )

    links = links_query.order_by(Link.created_at.desc()).all()

    return LinkListResponse(
        links=[LinkResponse.model_validate(link) for link in links],
        total=len(links)
    )


@app.get("/links/{slug}/stats", response_model=LinkStatsResponse)
def get_link_stats(slug: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.slug == slug).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    total_clicks = db.query(func.count(LinkClick.id)).filter(
        LinkClick.link_id == link.id
    ).scalar() or 0

    unique_clicks_approx = db.query(func.count(distinct(LinkClick.ip_hash))).filter(
        LinkClick.link_id == link.id
    ).scalar() or 0

    daily_stats = db.query(
        LinkClick.day,
        func.count(LinkClick.id).label('clicks'),
        func.count(distinct(LinkClick.ip_hash)).label('unique')
    ).filter(
        LinkClick.link_id == link.id
    ).group_by(LinkClick.day).order_by(LinkClick.day.desc()).all()

    daily = [
        DailyStats(date=stat.day, clicks=stat.clicks, unique=stat.unique)
        for stat in daily_stats
    ]

    return LinkStatsResponse(
        link=LinkBasic(
            id=link.id,
            slug=link.slug,
            target_url=link.target_url,
            created_at=link.created_at,
            is_disabled=link.is_disabled
        ),
        total_clicks=total_clicks,
        unique_clicks_approx=unique_clicks_approx,
        daily=daily
    )


@app.get("/{slug}")
def redirect_link(slug: str, request: Request, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.slug == slug).first()

    if not link or link.is_disabled:
        raise HTTPException(status_code=404, detail="Link not found")

    client_ip = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "")
    referrer = request.headers.get("referer", None)

    current_date = date.today()
    ip_hash_value = hash_ip(client_ip, user_agent, link.id, current_date)
    ip_truncated = truncate_ip(client_ip)

    click = LinkClick(
        link_id=link.id,
        referrer=referrer,
        user_agent=user_agent,
        ip_hash=ip_hash_value,
        ip_truncated_or_null=ip_truncated,
        day=current_date
    )

    db.add(click)
    db.commit()

    return RedirectResponse(url=link.target_url, status_code=status.HTTP_302_FOUND)
