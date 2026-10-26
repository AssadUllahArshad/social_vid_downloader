import pytest
from fastapi.testclient import TestClient
from yt_dlp import YoutubeDL

from app import main, tiktok_worker
from app.media_errors import MediaError, provider_error
from app.tiktok_download import native_download


def test_403_has_specific_sanitized_error():
    error = provider_error(Exception("HTTP Error 403 on https://cdn.tiktok.com/?secret=signed"), "tiktok")
    assert error.code == "platform_access_restricted"
    assert error.status == 502
    assert "secret" not in error.message


def test_raw_selector_not_client_input(memory_store):
    response = TestClient(main.app).post("/api/v1/download", json={"sessionId": "a" * 32, "formatId": "play"})
    assert response.status_code == 422


@pytest.mark.parametrize("raw_id", ["", "best/video", "play[height>0]", "../file"])
def test_unsafe_server_selectors_rejected(raw_id, tmp_path):
    record = {"selections": {"opaque": {"tracks": [{"format_id": raw_id}], "format": {"height": 720, "hasAudio": True}}}}
    with pytest.raises(MediaError):
        native_download(record, "opaque", tmp_path)


def test_fresh_native_download_validates_selected_id(monkeypatch, tmp_path):
    monkeypatch.setattr(YoutubeDL, "extract_info", lambda *a, **k: {"id": "sample", "formats": [{"format_id": "other"}]})
    with pytest.raises(MediaError, match="format changed"):
        tiktok_worker.download(
            {
                "source": "https://www.tiktok.com/@creator/video/6718335390845095173",
                "selector": "play",
                "directory": str(tmp_path),
                "height": 720,
                "hasAudio": True,
            }
        )


def test_manifest_not_delegated_to_unrestricted_ffmpeg(monkeypatch, tmp_path):
    monkeypatch.setattr(
        YoutubeDL, "extract_info", lambda *a, **k: {"id": "sample", "formats": [{"format_id": "play", "protocol": "m3u8_native"}]}
    )
    with pytest.raises(MediaError):
        tiktok_worker.download(
            {
                "source": "https://www.tiktok.com/@creator/video/6718335390845095173",
                "selector": "play",
                "directory": str(tmp_path),
                "height": 720,
                "hasAudio": True,
            }
        )


def test_unverified_public_fallback_is_not_called(monkeypatch):
    import http.cookiejar

    from app import extractor

    calls = []

    class Director:
        def close(self):
            pass

        def add_handler(self, handler):
            pass

    class Native:
        def __init__(self, options):
            self._request_director = Director()
            self.cookiejar = http.cookiejar.CookieJar()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def extract_info(self, url, download=False):
            calls.append(url)
            raise RuntimeError("HTTP Error 403")

    def forbidden(*args):
        raise AssertionError("An unverified TikTok parser must not become a fallback chain")

    monkeypatch.setattr(extractor, "YoutubeDL", Native)
    monkeypatch.setattr(extractor, "public_video_info", forbidden)
    with pytest.raises(MediaError) as error:
        extractor.extract_metadata("https://www.tiktok.com/@creator/video/6718335390845095173", "tiktok")
    assert error.value.code == "platform_access_restricted"
    assert len(calls) == 1
