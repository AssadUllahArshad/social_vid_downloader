import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import Settings


def test_untrusted_host_is_rejected():
    response = TestClient(main.app).get('/health', headers={'Host': 'attacker.invalid'})
    assert response.status_code == 400


def test_cors_explicit_origin(memory_store):
    client = TestClient(main.app)
    response = client.options('/api/v1/extract', headers={
        'Origin': 'https://socialviddownloader.com', 'Access-Control-Request-Method': 'POST'})
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'https://socialviddownloader.com'
    assert 'access-control-allow-credentials' not in response.headers
    response = client.options('/api/v1/extract', headers={
        'Origin': 'https://attacker.invalid', 'Access-Control-Request-Method': 'POST'})
    assert response.status_code == 400
    assert 'access-control-allow-origin' not in response.headers


@pytest.mark.parametrize('field', ['allowed_hosts', 'cors_origins'])
def test_production_rejects_wildcard_ingress(field):
    with pytest.raises(ValueError, match='explicit'):
        Settings(environment='production', state_backend='redis', database_url='postgresql+psycopg://operator:random@db/site',
                 ip_hash_secret='a' * 48, **{field: '*'})


def test_readiness_cache_outage_is_private(memory_store, monkeypatch):
    async def unavailable():
        raise RuntimeError('redis://private:secret@internal')
    monkeypatch.setattr(memory_store, 'ping', unavailable)
    response = TestClient(main.app).get('/ready')
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'not_ready'
    assert 'secret' not in response.text
    assert 'redis' not in response.text


def test_readiness_missing_media_binary(memory_store, monkeypatch):
    monkeypatch.setattr(main.shutil, 'which', lambda path: None)
    response = TestClient(main.app).get('/ready')
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'not_ready'
    assert 'ffmpeg' not in response.text.lower()
