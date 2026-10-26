from fastapi.testclient import TestClient

from app.main import app


def test_health():
    assert TestClient(app).get("/health").json() == {"status": "ok"}


def test_errors(memory_store):
    client = TestClient(app)
    assert client.post("/api/v1/extract", json={"url": "http://localhost"}).status_code == 400
    assert client.post("/api/v1/extract", json={"url": "https://youtu.be/not-an-id"}).status_code == 400
    assert client.post("/api/v1/extract", json={"url": "https://youtu.be/BaW_jenozKc", "platform": "instagram"}).status_code == 400
    assert client.post("/api/v1/extract", json={"url": "https://instagram.com/stories/user/123/"}).status_code == 501
    assert client.post("/api/v1/extract", json={"url": "https://snapchat.com/stories/example/"}).status_code == 501
    assert client.post("/api/v1/extract", content="x" * 9000).status_code == 413
    assert client.post("/api/v1/extract", json={}).status_code == 422
    assert client.post("/api/v1/extract", json={"url": "https://youtu.be/BaW_jenozKc", "password": "secret"}).status_code == 422


def test_rate_limit(memory_store, monkeypatch):
    async def exceeded(*args):
        return 21

    monkeypatch.setattr(memory_store, "increment", exceeded)
    response = TestClient(app).post("/api/v1/extract", json={"url": "https://youtu.be/BaW_jenozKc"})
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"


def test_limiter_fails_closed(memory_store, monkeypatch):
    async def unavailable(*args):
        raise ConnectionError("internal Redis connection details")

    monkeypatch.setattr(memory_store, "increment", unavailable)
    response = TestClient(app).post("/api/v1/extract", json={"url": "https://youtu.be/BaW_jenozKc"})
    assert response.status_code == 503
    assert "Redis" not in response.text


def test_untrusted_content_length(memory_store):
    response = TestClient(app).post("/api/v1/extract", content="x" * 9000, headers={"Content-Length": "1"})
    assert response.status_code == 413


def test_invalid_or_expired_download_tokens(memory_store):
    client = TestClient(app)
    assert client.get("/api/v1/jobs/not-a-token").status_code == 400
    assert client.get("/api/v1/files/" + "a" * 32).status_code == 410
    assert client.post("/api/v1/download", json={"sessionId": "a" * 32, "formatId": "b" * 20}).status_code == 410
