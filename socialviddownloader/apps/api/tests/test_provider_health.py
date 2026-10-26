from fastapi.testclient import TestClient

from app import main
from app.config import settings


def test_internal_status_requires_configured_admin_token(memory_store, monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(settings, "admin_provider_token", "")
    assert client.get("/internal/provider-status").status_code == 404
    monkeypatch.setattr(settings, "admin_provider_token", "test-administrator-access-token")
    assert client.get("/internal/provider-status").status_code == 401
    response = client.get("/internal/provider-status", headers={"Authorization": "Bearer test-administrator-access-token"})
    assert response.status_code == 200
    assert len(response.json()["providers"]) == 6
    tiktok = next(p for p in response.json()["providers"] if p["provider"] == "tiktok")
    assert tiktok["download"] == "degraded"
    assert "http" not in response.text


def test_public_capabilities_hide_internal_observations(memory_store):
    response = TestClient(main.app).get("/api/v1/capabilities")
    assert "lastFailureCategory" not in response.text
    assert "lastSuccessfulLiveTest" not in response.text
    snap = next(p for p in response.json()["providers"] if p["platform"] == "snapchat")
    assert snap["contentTypes"] == {"spotlight": "BETA", "story": "UNSUPPORTED", "shared": "BETA"}


def test_last_failure_retained_after_verified_success(memory_store):
    import asyncio

    from app.provider_health import observe

    async def check():
        await observe(memory_store, "tiktok", "extraction", False, "platform_access_restricted")
        await observe(memory_store, "tiktok", "extraction", True)
        await observe(memory_store, "tiktok", "download", True)
        record = await memory_store.get("provider-health:tiktok")
        assert record["lastTestStatus"] == "PASS"
        assert record["lastFailureCategory"] == "platform_access_restricted"
        assert record["lastSuccessfulLiveTest"]
        assert record["status"] == "degraded"
        assert record["download"] == "operational"

    asyncio.run(check())
