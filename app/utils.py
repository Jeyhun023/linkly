import random
import string
import hashlib
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Link

BASE62_CHARS = string.ascii_letters + string.digits

def generate_slug(length: int = 6) -> str:
    return ''.join(random.choices(BASE62_CHARS, k=length))

def generate_unique_slug(db: Session, max_attempts: int = 10) -> str:
    length = 6

    for attempt in range(max_attempts):
        slug = generate_slug(length)

        existing = db.query(Link).filter(Link.slug == slug).first()
        if not existing:
            return slug

        if attempt >= max_attempts // 2:
            length += 1

    raise ValueError("Failed to generate unique slug after maximum attempts")


def hash_ip(ip_address: str, user_agent: str, link_id: int, current_date: date) -> str:
    data = f"{ip_address}{user_agent}{link_id}{current_date.isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()
