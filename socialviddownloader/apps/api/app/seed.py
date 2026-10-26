import json
from pathlib import Path

from sqlalchemy import create_engine, delete, or_, select
from sqlalchemy.orm import Session

from .config import settings
from .models import FAQ, Keyword, KeywordCluster, Platform, SEOPage, Tool

RETIRED_SNAPCHAT_STORY_PATHS = {
    "/snapchat-story-downloader/",
    "/snapchat-story-viewer/",
    "/download-snapchat-story/",
    "/snap-story-downloader/",
}


def retire_snapchat_story_tools(db):
    """Retire legacy seed records without deleting editorial history."""
    story_page_ids = select(Tool.page_id).where(Tool.provider == "snapchat", Tool.content_type == "story")
    pages = db.scalars(select(SEOPage).where(or_(SEOPage.slug.in_(RETIRED_SNAPCHAT_STORY_PATHS), SEOPage.id.in_(story_page_ids)))).all()
    ids = {page.id for page in pages}
    for page in pages:
        page.status = "archived"
        page.indexable = False
        page.published_at = None
        page.schema_type = None
        page.related_pages = []
        page.internal_links = []
    db.execute(delete(Tool).where(Tool.page_id.in_(ids)))
    db.execute(delete(Keyword).where(Keyword.target_page_id.in_(ids)))
    db.execute(delete(FAQ).where(FAQ.page_id.in_(ids)))

    def retired_reference(value):
        from urllib.parse import urlsplit

        if isinstance(value, str):
            try:
                return urlsplit(value).path.rstrip("/") + "/" in RETIRED_SNAPCHAT_STORY_PATHS
            except ValueError:
                return False
        if isinstance(value, int):
            return value in ids
        if isinstance(value, dict):
            return any(retired_reference(v) for k, v in value.items() if k in {"url", "href", "slug", "pageId", "page_id", "id"})
        return False

    for page in db.scalars(select(SEOPage)):
        page.related_pages = [value for value in page.related_pages or [] if not retired_reference(value)]
        page.internal_links = [value for value in page.internal_links or [] if not retired_reference(value)]


def seed():
    records = json.loads((Path(__file__).resolve().parents[3] / "content/pages/tools.json").read_text())
    with Session(create_engine(settings.database_url)) as db:
        retire_snapchat_story_tools(db)
        if not db.scalar(select(SEOPage).where(SEOPage.slug == "/")):
            db.add(
                SEOPage(
                    slug="/",
                    name="Homepage",
                    page_type="home",
                    primary_intent="social video tool directory",
                    primary_keyword="social media video downloader",
                    title="SocialVidDownloader - Download Social Media Videos Online",
                    description="Find a dedicated tool for authorized social video downloads.",
                    h1="Download Social Media Videos Online",
                    introduction="A directory of platform-specific video tools.",
                    canonical="https://socialviddownloader.com/",
                    status="draft",
                )
            )
        for record in records:
            platform = db.scalar(select(Platform).where(Platform.slug == record["platform"].lower()))
            if not platform:
                platform = Platform(slug=record["platform"].lower(), name=record["platform"], capabilities={"enabled": False})
                db.add(platform)
                db.flush()
            slug = f"/{record['slug']}/"
            existing = db.scalar(select(SEOPage).where(SEOPage.slug == slug))
            if existing:
                if record["slug"] == "snapchat-downloader":
                    existing.description = record["description"]
                    existing.introduction = record["intro"]
                continue
            page = SEOPage(
                slug=slug,
                name=record["name"],
                platform_id=platform.id,
                primary_intent=record["slug"],
                primary_keyword=record["name"].lower(),
                title=record["name"],
                description=record["description"],
                h1=record["name"],
                introduction=record["intro"],
                canonical=f"https://socialviddownloader.com{slug}",
            )
            db.add(page)
            db.flush()
            cluster = db.scalar(select(KeywordCluster).where(KeywordCluster.name == platform.name))
            if not cluster:
                cluster = KeywordCluster(name=platform.name, intent="authorized video saving")
                db.add(cluster)
                db.flush()
            db.add(Tool(page_id=page.id, provider=platform.slug, content_type=record["kind"].lower() or "public"))
            db.add(Keyword(keyword=page.primary_keyword, intent="tool", target_page_id=page.id, cluster_id=cluster.id))
        db.commit()


if __name__ == "__main__":
    seed()
