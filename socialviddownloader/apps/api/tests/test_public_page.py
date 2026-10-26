import io
import json
from email.message import Message

import pytest

from app import public_page
from app.media_errors import MediaError


def fixture(monkeypatch, data, final="https://www.instagram.com/reel/wanted/"):
    headers = Message()
    headers["Content-Type"] = "text/html"
    html = '<meta property="og:title" content="Actual title"><script type="application/json">' + json.dumps(data) + "</script>"
    monkeypatch.setattr(public_page.SafeTransport, "open", lambda *a, **k: (io.BytesIO(html.encode()), headers, 200, final))


def test_only_requested_video_is_probed(monkeypatch):
    fixture(
        monkeypatch,
        {
            "shortcode": "wanted",
            "video_url": "https://cdninstagram.com/actual.mp4",
            "recommendation": {"__typename": "GraphVideo", "id": "other", "video_url": "https://cdninstagram.com/unrelated.mp4"},
        },
    )

    def measure(info, platform):
        assert [f["url"] for f in info["formats"]] == ["https://cdninstagram.com/actual.mp4"]
        info["formats"][0].update(height=854, width=480, vcodec="h264", acodec="aac")

    monkeypatch.setattr(public_page, "fill_missing_formats", measure)
    result = public_page.public_video_info("https://www.instagram.com/reel/wanted/", "instagram")
    assert result["title"] == "Actual title"
    assert result["formats"][0]["height"] == 854


def test_unrelated_video_never_becomes_success(monkeypatch):
    fixture(monkeypatch, {"shortcode": "other", "video_url": "https://cdninstagram.com/other.mp4"})
    with pytest.raises(MediaError, match="No media belonging"):
        public_page.public_video_info("https://www.instagram.com/reel/wanted/", "instagram")


def test_login_and_unmeasured_video_rejected(monkeypatch):
    fixture(monkeypatch, {}, "https://www.instagram.com/accounts/login/")
    with pytest.raises(MediaError, match="account or consent"):
        public_page.public_video_info("https://www.instagram.com/reel/wanted/", "instagram")
    fixture(monkeypatch, {"shortcode": "wanted", "video_url": "https://cdninstagram.com/actual.mp4"})
    monkeypatch.setattr(public_page, "fill_missing_formats", lambda *a: None)
    with pytest.raises(MediaError, match="could not be verified"):
        public_page.public_video_info("https://www.instagram.com/reel/wanted/", "instagram")
