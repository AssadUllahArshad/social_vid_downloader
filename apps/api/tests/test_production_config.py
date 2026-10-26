import time

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import main
from app.config import Settings


def production(**overrides):
    values = {"environment": "production", "database_url": "postgresql+psycopg://operator:unique-secret@db/site",
              "ip_hash_secret": "a" * 48, "state_backend": "redis"}
    values.update(overrides)
    return Settings(_env_file=None, **values)


@pytest.mark.parametrize("overrides", [
    {"ip_hash_secret": "local-development-only"},
    {"database_url": "postgresql+psycopg://socialvid:localdevelopment@db/site"},
    {"database_url": "sqlite:///test.db"},
    {"admin_provider_token": "short"},
    {"max_concurrent_jobs": 0},
    {"max_storage_bytes": 1},
    {"file_ttl_seconds": -1},
])
def test_unsafe_production_configuration_rejected(overrides):
    with pytest.raises(ValidationError):
        production(**overrides)


def test_development_defaults_to_sqlite_state_store():
    config = Settings(_env_file=None, environment="development")
    assert config.state_backend == "sqlite"


def test_production_allows_disabled_admin_and_private_redis():
    config = production(admin_provider_token="", redis_url="redis://private-redis:6379/0")
    assert config.environment == "production"
    assert config.admin_provider_token == ""


def test_storage_reservation_rejects_job_and_releases_slot(memory_store, monkeypatch):
    monkeypatch.setattr(main.settings, "max_file_bytes", 10)
    monkeypatch.setattr(main.settings, "max_storage_bytes", 15)
    monkeypatch.setattr(main, "download_plan", lambda *args: {"format": {"extension": "mp4"}, "selected_audio": []})
    token = "a" * 32
    memory_store.data["session:" + token] = ({"platform": "youtube"}, time.time() + 60)
    response = TestClient(main.app).post("/api/v1/download", json={"sessionId": token, "formatId": "b" * 20})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "storage_busy"
    assert not any(key.startswith("download-slot:") for key in memory_store.data)
    assert not main.tasks


def test_early_rate_limit_errors_have_security_headers(memory_store, monkeypatch):
    async def exceeded(*args):
        return 1000

    monkeypatch.setattr(memory_store, "increment", exceeded)
    response = TestClient(main.app).post("/api/v1/extract", json={"url": "https://youtu.be/BaW_jenozKc"})
    assert response.status_code == 429
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_bot_challenge_is_not_reported_as_private_content():
    from app.media_errors import provider_error

    failure = provider_error(Exception("Sign in to confirm you're not a bot. Use cookies-from-browser"), "youtube")
    assert failure.code == "platform_unavailable"
    assert failure.status == 502
    assert "cookies" not in failure.message
    assert "Private" not in failure.message


def test_public_capabilities_expose_notice_without_internal_diagnostics(memory_store):
    memory_store.data["provider-health:youtube"] = ({"status": "degraded", "lastFailureCategory": "secret internal diagnostic"}, time.time() + 60)
    response = TestClient(main.app).get("/api/v1/capabilities")
    assert response.status_code == 200
    provider = next(p for p in response.json()["providers"] if p["platform"] == "youtube")
    assert "public videos" in provider["availabilityNotice"]
    assert "secret internal" not in response.text


def test_stale_cleanup_preserves_active_media_and_outside_symlinks(tmp_path):
    import os

    root = tmp_path / "media"
    root.mkdir()
    stale = root / ("a" * 32)
    stale.mkdir()
    (stale / "movie.mp4").write_bytes(b"expired media")
    os.utime(stale, (1, 1))
    active = root / ("b" * 32)
    active.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep").write_bytes(b"untouched")
    (root / ("c" * 32)).symlink_to(outside, target_is_directory=True)
    main.sweep_stale_media(root, time.time(), 600)
    assert not stale.exists()
    assert active.exists()
    assert (outside / "keep").exists()
    main.sweep_stale_media(root, time.time(), 600)
