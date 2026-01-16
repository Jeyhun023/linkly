from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date

from app.db import get_db
from app.models import Link, LinkClick
from app.utils import hash_ip

router = APIRouter(tags=["redirect"])

@router.get("/{slug}")
def redirect_link(slug: str, request: Request, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.slug == slug, Link.is_disabled == False).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    referrer = request.headers.get("referer", None)

    current_date = date.today()
    ip_hash_value = hash_ip(ip_address or "", user_agent, link.id, current_date)

    click = LinkClick(
        link_id=link.id,
        referrer=referrer,
        user_agent=user_agent,
        ip_hash=ip_hash_value,
        ip_address=ip_address,
        day=current_date
    )

    db.add(click)
    db.commit()

    return RedirectResponse(url=link.target_url, status_code=status.HTTP_302_FOUND)
