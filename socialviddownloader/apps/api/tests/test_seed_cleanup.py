from datetime import datetime, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import FAQ, Base, Keyword, KeywordCluster, Platform, SEOPage, Tool
from app.seed import seed


def test_seed_has_no_public_snapchat_story(monkeypatch, tmp_path):
    database = f"sqlite:///{tmp_path / 'inventory.sqlite'}"
    monkeypatch.setattr(settings, "database_url", database)
    engine = create_engine(database)
    Base.metadata.create_all(engine)
    seed()
    seed()
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(Tool)) == 11
        assert db.scalar(select(SEOPage).where(SEOPage.slug == "/snapchat-story-downloader/")) is None
        assert db.scalar(select(Tool).where(Tool.provider == "snapchat", Tool.content_type == "spotlight"))
        assert db.scalar(select(Tool).where(Tool.provider == "snapchat", Tool.content_type == "story")) is None


def test_existing_seed_story_archived_and_public_references_removed(monkeypatch, tmp_path):
    database = f"sqlite:///{tmp_path / 'legacy-inventory.sqlite'}"
    monkeypatch.setattr(settings, "database_url", database)
    engine = create_engine(database)
    Base.metadata.create_all(engine)
    seed()
    with Session(engine) as db:
        platform = db.scalar(select(Platform).where(Platform.slug == "snapchat"))
        old = SEOPage(
            slug="/snapchat-story-downloader/",
            name="Snapchat Story Downloader",
            platform_id=platform.id,
            primary_intent="snapchat-story-downloader",
            primary_keyword="snapchat story downloader",
            title="Snapchat Story Downloader",
            description="Legacy seed",
            h1="Legacy",
            introduction="Legacy",
            canonical="https://socialviddownloader.com/snapchat-story-downloader/",
            status="published",
            indexable=True,
            published_at=datetime.now(timezone.utc),
            schema_type="SoftwareApplication",
        )
        db.add(old)
        db.flush()
        retired_id = old.id
        db.add(Tool(page_id=old.id, provider="snapchat", content_type="story", enabled=True))
        cluster = db.scalar(select(KeywordCluster).where(KeywordCluster.name == "Snapchat"))
        db.add(Keyword(keyword="download snapchat story", intent="tool", target_page_id=old.id, cluster_id=cluster.id))
        db.add(FAQ(page_id=old.id, question="Legacy question", answer="Legacy answer"))
        spotlight = db.scalar(select(SEOPage).where(SEOPage.slug == "/snapchat-spotlight-downloader/"))
        spotlight.internal_links = [{"href": old.slug}, {"href": "/youtube-video-downloader/"}]
        spotlight.related_pages = [old.id]
        db.commit()
    seed()
    seed()
    with Session(engine) as db:
        old = db.get(SEOPage, retired_id)
        assert old.status == "archived" and not old.indexable
        assert old.published_at is None and old.schema_type is None
        assert db.scalar(select(Tool).where(Tool.page_id == retired_id)) is None
        assert db.scalar(select(Keyword).where(Keyword.target_page_id == retired_id)) is None
        assert db.scalar(select(FAQ).where(FAQ.page_id == retired_id)) is None
        spotlight = db.scalar(select(SEOPage).where(SEOPage.slug == "/snapchat-spotlight-downloader/"))
        assert spotlight.related_pages == []
        assert spotlight.internal_links == [{"href": "/youtube-video-downloader/"}]
        assert db.scalar(select(KeywordCluster).where(KeywordCluster.name == "Snapchat"))
