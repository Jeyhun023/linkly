from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db
from app.schemas import HealthResponse, LinkCreateRequest, LinkCreateResponse
from app.models import Link
from app.utils import generate_unique_slug
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
