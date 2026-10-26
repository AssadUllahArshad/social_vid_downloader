"""Initial editorial and provider schema, frozen for reproducible migrations."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(254), unique=True, nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(24), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "platforms",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(64), unique=True, nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("capabilities", sa.JSON(), nullable=False),
    )
    op.create_table(
        "seo_pages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("page_type", sa.String(32), nullable=False),
        sa.Column("platform_id", sa.Integer(), sa.ForeignKey("platforms.id"), nullable=True),
        sa.Column("primary_intent", sa.String(255), unique=True, nullable=False),
        sa.Column("primary_keyword", sa.String(255), nullable=False),
        sa.Column("secondary_keywords", sa.JSON(), nullable=False),
        sa.Column("title", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("h1", sa.String(255), nullable=False),
        sa.Column("introduction", sa.Text(), nullable=False),
        sa.Column("body", sa.JSON(), nullable=False),
        sa.Column("canonical", sa.String(512), unique=True, nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("indexable", sa.Boolean(), nullable=False),
        sa.Column("schema_type", sa.String(64), nullable=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("related_pages", sa.JSON(), nullable=False),
        sa.Column("internal_links", sa.JSON(), nullable=False),
        sa.Column("og_metadata", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("content_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "tools",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("page_id", sa.Integer(), sa.ForeignKey("seo_pages.id"), unique=True, nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "blog_posts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("page_id", sa.Integer(), sa.ForeignKey("seo_pages.id"), unique=True, nullable=False),
        sa.Column("references", sa.JSON(), nullable=False),
    )
    op.create_table(
        "keyword_clusters",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("intent", sa.String(255), nullable=False),
    )
    op.create_table(
        "keywords",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("keyword", sa.String(255), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.Numeric(5, 2), nullable=True),
        sa.Column("cpc", sa.Numeric(10, 2), nullable=True),
        sa.Column("country", sa.String(2), nullable=False),
        sa.Column("intent", sa.String(64), nullable=False),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("keyword_clusters.id"), nullable=True),
        sa.Column("target_page_id", sa.Integer(), sa.ForeignKey("seo_pages.id"), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
    )
    op.create_table(
        "faqs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("page_id", sa.Integer(), sa.ForeignKey("seo_pages.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    op.create_table(
        "redirects",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source", sa.String(255), unique=True, nullable=False),
        sa.Column("destination", sa.String(512), nullable=False),
        sa.Column("status", sa.Integer(), nullable=False),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("redirects")
    op.drop_table("faqs")
    op.drop_table("keywords")
    op.drop_table("keyword_clusters")
    op.drop_table("blog_posts")
    op.drop_table("tools")
    op.drop_table("seo_pages")
    op.drop_table("platforms")
    op.drop_table("users")
