import random
import string
from sqlalchemy.orm import Session
from app.models import Link

BASE62_CHARS = string.ascii_letters + string.digits


def generate_slug(length: int = 6) -> str:
    """Generate a random base62 slug."""
    return ''.join(random.choices(BASE62_CHARS, k=length))


def generate_unique_slug(db: Session, max_attempts: int = 10) -> str:
    """
    Generate a unique slug that doesn't exist in the database.
    Starts with length 6, increases if collisions occur.
    """
    length = 6

    for attempt in range(max_attempts):
        slug = generate_slug(length)

        existing = db.query(Link).filter(Link.slug == slug).first()
        if not existing:
            return slug

        if attempt >= max_attempts // 2:
            length += 1

    raise ValueError("Failed to generate unique slug after maximum attempts")
