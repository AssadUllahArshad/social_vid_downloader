import pytest

from app.formats import normalize
from app.media_errors import MediaError


def video(height, identifier, **kwargs):
    return {
        "height": height,
        "width": 640,
        "format_id": identifier,
        "url": "https://media.googlevideo.com/file",
        "ext": "mp4",
        "vcodec": "avc1",
        "acodec": "mp4a",
        "protocol": "https",
        **kwargs,
    }


def test_only_real_formats_and_duplicates():
    result, private = normalize(
        {
            "formats": [
                video(360, "low"),
                video(720, "hd"),
                video(720, "duplicate", vcodec="av01"),
                video(2160, "drm", has_drm=True),
                video(1080, "manifest", protocol="m3u8_native"),
            ]
        },
        100000000,
    )
    assert [f["height"] for f in result] == [720, 360]
    assert all(f["filesize"] is None for f in result)
    assert "hd" in str(private)
    assert all("url" not in f for f in result)


def test_merge_and_estimates():
    formats = [
        video(1080, "v", acodec="none", filesize=1000),
        {"format_id": "a", "url": "https://media.googlevideo.com/audio", "vcodec": "none", "acodec": "mp4a", "ext": "m4a", "filesize": 200},
    ]
    public, private = normalize({"formats": formats}, 100000000)
    assert public[0]["requiresMerge"]
    assert public[0]["filesize"] is None
    assert public[0]["estimatedFilesize"] == 1200
    assert len(private[public[0]["id"]]["tracks"]) == 2
    formats[1].pop("filesize")
    public, _ = normalize({"formats": formats}, 100000000)
    assert public[0]["estimatedFilesize"] is None


def test_silent_video_is_labeled_truthfully():
    public, _ = normalize({"formats": [video(360, "silent", acodec="none")]}, 100000000)
    assert public[0]["hasAudio"] is False


def test_live_and_no_formats():
    with pytest.raises(MediaError):
        normalize({"is_live": True}, 1000)
    with pytest.raises(MediaError):
        normalize({"formats": []}, 1000)


def test_4k_label_requires_real_4k_dimensions():
    portrait, _ = normalize({"formats": [video(2160, "portrait", width=1215)]}, 100000000)
    assert "4K" not in portrait[0]["quality"]
    landscape, _ = normalize({"formats": [video(2160, "landscape", width=3840)]}, 100000000)
    assert landscape[0]["quality"] == "2160p 4K"
