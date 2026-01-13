from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Boolean, Date, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(BigInteger, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    target_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)
    campaign = Column(String, nullable=True)
    label = Column(String, nullable=True)
    source = Column(String, nullable=True)
    is_disabled = Column(Boolean, default=False, nullable=False)

    clicks = relationship("LinkClick", back_populates="link")

    __table_args__ = (
        Index('idx_links_slug', 'slug', unique=True),
    )


class LinkClick(Base):
    __tablename__ = "link_clicks"

    id = Column(BigInteger, primary_key=True, index=True)
    link_id = Column(BigInteger, ForeignKey('links.id'), nullable=False)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    referrer = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    ip_hash = Column(String, nullable=False)
    ip_truncated_or_null = Column(String, nullable=True)
    day = Column(Date, nullable=False)

    link = relationship("Link", back_populates="clicks")

    __table_args__ = (
        Index('idx_link_clicks_link_id_clicked_at', 'link_id', 'clicked_at'),
        Index('idx_link_clicks_link_id_ip_hash', 'link_id', 'ip_hash'),
    )
