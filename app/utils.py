import random
import string
import hashlib
from datetime import date
from typing import Optional
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


def hash_ip(ip_address: str, user_agent: str, link_id: int, current_date: date) -> str:
    """
    Create a privacy-safe hash of IP address with salt.
    Hash = SHA256(IP + user_agent + link_id + current_date)
    """
    data = f"{ip_address}{user_agent}{link_id}{current_date.isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()


def truncate_ip(ip_address: str) -> Optional[str]:
    """
    Truncate IP address for privacy.
    IPv4: Keep first 3 octets (e.g., 192.168.1.xxx)
    IPv6: Keep first 4 groups (e.g., 2001:db8:85a3:8d3:xxxx:xxxx:xxxx:xxxx)
    """
    if '.' in ip_address:
        parts = ip_address.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"
    elif ':' in ip_address:
        parts = ip_address.split(':')
        if len(parts) >= 4:
            return ':'.join(parts[:4]) + ':xxxx:xxxx:xxxx:xxxx'
    return None
