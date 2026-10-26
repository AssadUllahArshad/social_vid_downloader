import socket

import pytest

from app.media_errors import MediaError
from app.security import InvalidUrl, validate_media_url
from app.transport import BoundedResponse, PinnedHTTPS, SafeTransport, destination


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=BaW_jenozKc",
        "https://youtube.com/shorts/BGQWPY4IigY",
        "https://facebook.com/watch/?v=123",
        "https://facebook.com/reel/123/",
        "https://instagram.com/p/Example123/",
        "https://instagram.com/reel/Example123/",
        "https://tiktok.com/@creator/video/123456/",
    ],
)
def test_supported_content_types(url):
    assert validate_media_url(url)[1] in {"youtube", "facebook", "instagram", "tiktok"}


@pytest.mark.parametrize(
    "url",
    [
        "https://youtube.com/playlist?list=123",
        "https://instagram.com/creator/",
        "https://facebook.com/profile.php?id=1",
        "https://tiktok.com/@creator",
    ],
)
def test_profile_collection_rejection(url):
    with pytest.raises(InvalidUrl):
        validate_media_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "https://googlevideo.com.attacker.test/",
        "https://youtube.com@127.0.0.1/",
        "https://youtube.com:8080/",
        "file:///etc/passwd",
    ],
)
def test_outbound_allowlist(url):
    with pytest.raises(MediaError):
        destination(url, "youtube")


def test_dns_mixed_addresses():
    with pytest.raises(MediaError):
        destination(
            "https://youtube.com", "youtube", resolver=lambda *a, **k: [(0, 0, 0, 0, ("8.8.8.8", 443)), (0, 0, 0, 0, ("127.0.0.1", 443))]
        )


def test_connect_is_pinned(monkeypatch):
    calls = []

    class Context:
        def wrap_socket(self, sock, server_hostname):
            calls.append(server_hostname)
            return sock

    connection = PinnedHTTPS("youtube.com", ["8.8.8.8"], 443, 1)
    connection._context = Context()
    monkeypatch.setattr(socket, "create_connection", lambda target, timeout: calls.append(target) or object())
    connection.connect()
    assert calls == [("8.8.8.8", 443), "youtube.com"]


def test_redirect_to_metadata_is_rejected(monkeypatch):
    import app.transport as transport

    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(0, 0, 0, 0, ("8.8.8.8", 443))])

    class Reply:
        status = 302

        def getheader(self, name):
            return "http://169.254.169.254/latest/meta-data"

        def close(self):
            pass

    class Connection:
        def __init__(self, *a):
            pass

        def request(self, *a, **k):
            pass

        def getresponse(self):
            return Reply()

        def close(self):
            pass

    monkeypatch.setattr(transport, "PinnedHTTPS", Connection)
    with pytest.raises(MediaError):
        SafeTransport("youtube").open("https://youtube.com/watch")


def test_body_limit_without_content_length():
    import io

    class Connection:
        def close(self):
            pass

    bounded = BoundedResponse(io.BytesIO(b"a" * 11), Connection(), 10)
    with pytest.raises(MediaError):
        bounded.read()
