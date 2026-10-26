#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR/apps/api"
TEST_DATABASE_FILE="$(mktemp /tmp/socialvid-db.XXXXXX)"
trap 'rm -f "$TEST_DATABASE_FILE"' EXIT
export DATABASE_URL="sqlite:///$TEST_DATABASE_FILE"
export PYTHONPYCACHEPREFIX=/tmp/socialvid-pycache
.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed
.venv/bin/python -m app.seed
.venv/bin/alembic check
.venv/bin/python - <<'PY'
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from app.config import settings
from app.models import SEOPage, Platform, Tool, Keyword
with Session(create_engine(settings.database_url)) as session:
    for model, expected in [(SEOPage, 12), (Platform, 6), (Tool, 11), (Keyword, 11)]:
        assert session.scalar(select(func.count()).select_from(model)) == expected
    assert session.scalar(select(func.count()).select_from(SEOPage).where(SEOPage.indexable)) == 0
print('Migration, schema consistency, and idempotent seed checks passed.')
PY
.venv/bin/alembic downgrade base
