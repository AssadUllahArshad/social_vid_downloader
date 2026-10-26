import asyncio

import pytest
from pydantic import ValidationError

from app.config import Settings, settings
from app.store import SQLiteStore


def test_sqlite_lease_release_cannot_delete_new_owner(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "local_state_path", str(tmp_path / "state.sqlite"))

    async def check():
        store = SQLiteStore()
        assert await store.set("slot", "new-owner", 60, nx=True)
        assert not await store.compare_delete("slot", "old-owner")
        assert await store.get("slot") == "new-owner"
        assert await store.compare_delete("slot", "new-owner")
        assert await store.get("slot") is None

    asyncio.run(check())


def test_sqlite_rejected_in_production():
    with pytest.raises(ValidationError, match="only in development"):
        Settings(_env_file=None, environment="production", state_backend="sqlite")
