import io
import json

import pytest
from fastapi.testclient import TestClient
from yt_dlp import YoutubeDL

from app import main
from app.media_errors import MediaError
from app.providers.snapchat import PublicSpotlightIE, provider
from app.security import InvalidUrl, validate_media_url
from app.transport import SafeTransport, destination


@pytest.mark.parametrize(
    "url,kind",
    [
        ("https://www.snapchat.com/spotlight/ABC_123", "spotlight"),
        ("https://snapchat.com/t/AbCd1234", "shared"),
        ("https://www.snapchat.com/t/AbCd1234", "shared"),
        ("https://snapchat.com/@creator/spotlight/ABC-def_123", "spotlight"),
        ("https://www.snapchat.com/@creator/spotlight/ABC-def_123?locale=en_US", "spotlight"),
        ("https://snapchat.com/add/creator", "profile"),
        ("https://snapchat.com/@creator", "profile"),
        ("https://www.snapchat.com/stories/creator/story_123", "story"),
    ],
)
def test_legitimate_url_detection(url, kind):
    assert validate_media_url(url)[1:] == ("snapchat", kind)


@pytest.mark.parametrize(
    "url",
    [
        "https://snapchat.com.evil.test/spotlight/a",
        "https://evil.snapchat.com/spotlight/a",
        "https://snapchat.com/accounts/login",
        "https://snapchat.com/spotlight/",
        "https://snapchat.com/@creator/spotlight/a/extra",
        "https://snapchat.com/@creator/spotlight/%2fadmin",
    ],
)
def test_invalid_domain_or_account_url(url):
    with pytest.raises(InvalidUrl):
        validate_media_url(url)


def test_stories_and_credentials_unavailable(memory_store):
    client = TestClient(main.app)
    response = client.post("/api/v1/extract", json={"url": "https://snapchat.com/stories/creator/story"})
    assert response.status_code == 501
    assert response.json()["error"]["code"] == "content_unsupported"
    assert client.post("/api/v1/extract", json={"url": "https://snapchat.com/spotlight/abc", "cookies": "private"}).status_code == 422
    with pytest.raises(MediaError, match="Only public Spotlight"):
        provider.extract("https://snapchat.com/stories/creator/story")


def test_share_redirect_must_resolve_to_spotlight(monkeypatch):
    from app.providers.snapchat import resolve_public_spotlight

    monkeypatch.setattr(SafeTransport, "open", lambda *a, **k: (io.BytesIO(b""), {}, 200, "https://snapchat.com/spotlight/abc"))
    assert resolve_public_spotlight("https://snapchat.com/t/share").endswith("/spotlight/abc")
    monkeypatch.setattr(SafeTransport, "open", lambda *a, **k: (io.BytesIO(b""), {}, 200, "https://snapchat.com/stories/user/story"))
    with pytest.raises(MediaError):
        resolve_public_spotlight("https://snapchat.com/t/share")


def test_snapchat_cdn_private_address_blocked():
    def resolver(*a, **k):
        return [(2, 1, 6, "", ("127.0.0.1", 443))]

    with pytest.raises(MediaError):
        destination("https://cf-st.sc-cdn.net/file", "snapchat", resolver)
    with pytest.raises(MediaError):
        destination("https://unapproved.test/file", "snapchat", resolver)


def test_public_page_metadata_belongs_to_requested_spotlight(monkeypatch):
    def entry(identifier, title):
        return {
            "story": {"storyId": {"value": identifier}},
            "metadata": {
                "videoMetadata": {
                    "name": title,
                    "contentUrl": "https://cf-st.sc-cdn.net/public.mp4",
                    "width": 480,
                    "height": 880,
                    "durationMs": 4665,
                    "creator": {"personCreator": {"username": "creator"}},
                }
            },
        }

    data = {"props": {"pageProps": {"spotlightFeed": {"spotlightStories": [entry("wanted", "Wrong"), entry("wanted-full_id", "Actual")]}}}}
    with YoutubeDL({"quiet": True}) as ydl:
        ie = PublicSpotlightIE(ydl)
        monkeypatch.setattr(
            ie, "_download_webpage", lambda *a, **k: '<script id="__NEXT_DATA__" type="application/json">' + json.dumps(data) + "</script>"
        )
        info = ie._real_extract("https://snapchat.com/@creator/spotlight/wanted-full_id")
    assert info["id"] == "wanted-full_id"
    assert info["title"] == "Actual"
    assert info["height"] == 880
    assert info["duration"] == 4.665
    assert info["uploader"] == "creator"


@pytest.mark.parametrize("prefix", ["", "www."])
def test_creator_url_and_full_hyphenated_id(prefix):
    url = f"https://{prefix}snapchat.com/@creator/spotlight/ABC-def_123?locale=en_US"
    assert PublicSpotlightIE._match_id(url) == "ABC-def_123"


@pytest.mark.parametrize("final,code", [
    ("https://snapchat.com/stories/user/story", "content_unsupported"),
    ("https://snapchat.com/@user", "snapchat_profile"),
    ("https://snapchat.com/add/user", "snapchat_profile"),
    ("https://snapchat.com/accounts/login", "snapchat_restricted"),
    ("https://snapchat.com/download", "snapchat_not_spotlight"),
    ("https://snapchat.com/t/unresolved", "snapchat_not_spotlight"),
])
def test_share_classifies_unsupported_destination(monkeypatch, final, code):
    from app.providers.snapchat import resolve_public_spotlight

    monkeypatch.setattr(SafeTransport, "open", lambda *a, **k: (io.BytesIO(b""), {}, 200, final))
    with pytest.raises(MediaError) as failure:
        resolve_public_spotlight("https://snapchat.com/t/share")
    assert failure.value.code == code


@pytest.mark.parametrize("status,code", [(401,"snapchat_restricted"), (403,"snapchat_restricted"), (404,"snapchat_unavailable"),
                                       (410,"snapchat_unavailable"), (429,"snapchat_temporary"), (503,"snapchat_temporary")])
def test_share_http_failures(monkeypatch, status, code):
    from app.providers.snapchat import resolve_public_spotlight

    body = io.BytesIO(b"")
    monkeypatch.setattr(SafeTransport, "open", lambda *a, **k: (body, {}, status, "https://snapchat.com/t/share"))
    with pytest.raises(MediaError) as failure:
        resolve_public_spotlight("https://snapchat.com/t/share")
    assert failure.value.code == code
    assert body.closed


def test_story_and_profile_rejected_before_extraction(memory_store, monkeypatch):
    monkeypatch.setattr("app.runner.isolated_extract", lambda *a: pytest.fail("Unsupported content must never reach extraction"))
    client = TestClient(main.app)
    for url, code in [("https://snapchat.com/stories/user/story", "content_unsupported"),
                      ("https://snapchat.com/@user", "snapchat_profile")]:
        result = client.post("/api/v1/extract", json={"url":url,"platform":"snapchat","contentType":"spotlight"})
        assert result.status_code == 501
        assert result.json()["error"]["code"] == code


@pytest.mark.parametrize("restricted,code", [(False,"snapchat_extraction_failed"), (True,"snapchat_restricted")])
def test_no_fallback_to_recommended_or_restricted_video(monkeypatch, restricted, code):
    data = {"props":{"pageProps":{"restricted":restricted,"spotlightFeed":{"spotlightStories":[]}}}}
    with YoutubeDL({"quiet":True}) as ydl:
        ie = PublicSpotlightIE(ydl)
        monkeypatch.setattr(ie, "_download_webpage", lambda *a, **k: '<script id="__NEXT_DATA__">'+json.dumps(data)+'</script>')
        with pytest.raises(MediaError) as failure:
            ie._real_extract("https://snapchat.com/@creator/spotlight/wanted-full_id")
        assert failure.value.code == code


@pytest.mark.parametrize("redirect", ["http://169.254.169.254/latest/meta-data", "https://evil.test/video", "https://www.youtube.com/watch?v=abc"])
def test_share_redirect_cannot_escape_snapchat_transport(monkeypatch, redirect):
    import socket

    import app.transport as transport
    from app.providers.snapchat import resolve_public_spotlight

    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    requests = []

    class Response:
        status = 302

        def getheader(self, name):
            return redirect

        def close(self):
            pass

    class Connection:
        def __init__(self, *a):
            pass

        def request(self, *a, **k):
            requests.append(a)

        def getresponse(self):
            return Response()

        def close(self):
            pass

    monkeypatch.setattr(transport, "PinnedHTTPS", Connection)
    with pytest.raises(MediaError) as failure:
        resolve_public_spotlight("https://snapchat.com/t/share")
    assert failure.value.code == "unsafe_destination"
    assert len(requests) == 1


@pytest.mark.parametrize("message,code", [
    ("HTTP Error 503: Service Unavailable", "snapchat_temporary"),
    ("Unable to download webpage: connection refused", "snapchat_temporary"),
    ("HTTP Error 403: Forbidden", "snapchat_restricted"),
    ("HTTP Error 404: Not Found", "snapchat_unavailable"),
    ("Unable to extract video metadata", "snapchat_extraction_failed"),
])
def test_direct_extraction_errors_keep_distinct_categories(monkeypatch, message, code):
    from app.extractor import extract_metadata

    monkeypatch.setattr("app.providers.snapchat.resolve_public_spotlight", lambda url: url)

    def fail(*args, **kwargs):
        raise RuntimeError(message)

    monkeypatch.setattr(YoutubeDL, "extract_info", fail)
    with pytest.raises(MediaError) as failure:
        extract_metadata("https://snapchat.com/spotlight/full-id", "snapchat")
    assert failure.value.code == code
