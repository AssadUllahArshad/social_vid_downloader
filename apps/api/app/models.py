from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Timestamps:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


class User(Timestamps, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(24), default="editor")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Platform(Base):
    __tablename__ = "platforms"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    capabilities: Mapped[dict] = mapped_column(JSON, default=dict)


class SEOPage(Timestamps, Base):
    __tablename__ = "seo_pages"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    page_type: Mapped[str] = mapped_column(String(32), default="tool")
    platform_id: Mapped[Optional[int]] = mapped_column(ForeignKey("platforms.id"))
    primary_intent: Mapped[str] = mapped_column(String(255), unique=True)
    primary_keyword: Mapped[str] = mapped_column(String(255))
    secondary_keywords: Mapped[list] = mapped_column(JSON, default=list)
    title: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text)
    h1: Mapped[str] = mapped_column(String(255))
    introduction: Mapped[str] = mapped_column(Text)
    body: Mapped[list] = mapped_column(JSON, default=list)
    canonical: Mapped[str] = mapped_column(String(512), unique=True)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    indexable: Mapped[bool] = mapped_column(Boolean, default=False)
    schema_type: Mapped[Optional[str]] = mapped_column(String(64))
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    related_pages: Mapped[list] = mapped_column(JSON, default=list)
    internal_links: Mapped[list] = mapped_column(JSON, default=list)
    og_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    content_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Tool(Base):
    __tablename__ = "tools"
    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("seo_pages.id"), unique=True)
    provider: Mapped[str] = mapped_column(String(64))
    content_type: Mapped[str] = mapped_column(String(64))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)


class BlogPost(Base):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("seo_pages.id"), unique=True)
    references: Mapped[list] = mapped_column(JSON, default=list)


class KeywordCluster(Base):
    __tablename__ = "keyword_clusters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    intent: Mapped[str] = mapped_column(String(255))


class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255))
    volume: Mapped[Optional[int]] = mapped_column(Integer)
    difficulty: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    cpc: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    country: Mapped[str] = mapped_column(String(2), default="US")
    intent: Mapped[str] = mapped_column(String(64))
    cluster_id: Mapped[Optional[int]] = mapped_column(ForeignKey("keyword_clusters.id"))
    target_page_id: Mapped[Optional[int]] = mapped_column(ForeignKey("seo_pages.id"))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")


class FAQ(Base):
    __tablename__ = "faqs"
    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("seo_pages.id"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, default=0)


class Redirect(Base):
    __tablename__ = "redirects"
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(255), unique=True)
    destination: Mapped[str] = mapped_column(String(512))
    status: Mapped[int] = mapped_column(Integer, default=301)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(64))
    entity: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
