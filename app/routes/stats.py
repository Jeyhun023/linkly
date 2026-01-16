from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.db import get_db
from app.schemas import LinkStatsResponse, LinkBasic, DailyStats
from app.models import Link, LinkClick

router = APIRouter(prefix="/links", tags=["stats"])

@router.get("/{slug}/stats", response_model=LinkStatsResponse)
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
