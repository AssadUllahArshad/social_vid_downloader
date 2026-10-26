import io
import shutil
import subprocess
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main
from app.formats import normalize
from app.media import generate_file, safe_filename
from app.media_errors import MediaError
from app.probe import inspect_file
from app.transport import SafeTransport


@pytest.fixture(scope="module")
def real_media(tmp_path_factory):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.fail("FFmpeg and FFprobe are required for full-pipeline tests")
    folder = tmp_path_factory.mktemp("real-media")
    common = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi"]
    subprocess.run(
        common
        + [
            "-i",
            "testsrc=size=160x90:rate=10",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440",
            "-t",
            "1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(folder / "combined.mp4"),
        ],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(folder / "combined.mp4"), "-an", "-c:v", "copy", str(folder / "video.mp4")], check=True
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(folder / "combined.mp4"), "-vn", "-c:a", "copy", str(folder / "audio.m4a")], check=True
    )
    return {name: (folder / name).read_bytes() for name in ["combined.mp4", "video.mp4", "audio.m4a"]}


def record(platform, merge=False):
    formats = [
        {
            "format_id": "v",
            "height": 90,
            "width": 160,
            "vcodec": "avc1",
            "acodec": "none" if merge else "mp4a",
            "ext": "mp4",
            "url": "https://fixture.invalid/" + ("video.mp4" if merge else "combined.mp4"),
        }
    ]
    if merge:
        formats.append({"format_id": "a", "vcodec": "none", "acodec": "mp4a", "ext": "m4a", "url": "https://fixture.invalid/audio.m4a"})
    public, selections = normalize({"formats": formats}, 10000000)
    return {
        "metadata": {
            "title": "Integration fixture",
            "creator": None,
            "duration": 1,
            "thumbnailSource": None,
            "platform": platform,
            "formats": public,
        },
        "selections": selections,
        "platform": platform,
        "source": "test fixture",
    }


@pytest.fixture
def fixture_transport(monkeypatch, real_media):
    def open_media(self, url, **kwargs):
        data = real_media[Path(url).name]
        return io.BytesIO(data), {}, 200, url

    monkeypatch.setattr(SafeTransport, "open", open_media)


@pytest.mark.parametrize(
    "platform,kind,url",
    [
        ("snapchat", "spotlight", "https://snapchat.com/spotlight/abc123"),
        ("youtube", "video", "https://youtube.com/watch?v=BaW_jenozKc"),
        ("youtube", "shorts", "https://youtube.com/shorts/BGQWPY4IigY"),
        ("facebook", "video", "https://facebook.com/watch/?v=123"),
        ("facebook", "reels", "https://facebook.com/reel/123"),
        ("instagram", "video", "https://instagram.com/p/Example123/"),
        ("instagram", "reels", "https://instagram.com/reel/Example123/"),
        ("tiktok", "video", "https://tiktok.com/@creator/video/123456"),
    ],
)
def test_real_file_pipeline_all_tool_types(platform, kind, url, memory_store, fixture_transport, monkeypatch):
    source = record(platform)
    monkeypatch.setattr(main.providers[platform], "extract", lambda url: source)
    with TestClient(main.app) as client:
        response = client.post("/api/v1/extract", json={"url": url, "platform": platform, "contentType": kind})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] and data["thumbnail"] is None
        assert "fixture.invalid" not in response.text
        assert len(data["formats"]) == 1
        prepared = client.post("/api/v1/download", json={"sessionId": data["sessionId"], "formatId": data["formats"][0]["id"]})
        assert prepared.status_code == 202
        job_id = prepared.json()["jobId"]
        for _ in range(100):
            job = client.get("/api/v1/jobs/" + job_id).json()
            if job["status"] in {"ready", "error"}:
                break
            time.sleep(0.05)
        assert job["status"] == "ready", job
        saved = client.get("/api/v1/files/" + job_id)
        assert saved.status_code == 200
        assert len(saved.content) == job["filesize"]
        assert "attachment" in saved.headers["Content-Disposition"]
        ranged = client.get("/api/v1/files/" + job_id, headers={"Range": "bytes=0-31"})
        assert ranged.status_code == 206
        assert len(ranged.content) == 32


def test_actual_ffmpeg_merge(fixture_transport, tmp_path):
    source = record("youtube", True)
    result = generate_file(source, source["metadata"]["formats"][0]["id"], tmp_path / "merge")
    measured = inspect_file(result["path"])
    assert {s["codec_type"] for s in measured["streams"]} >= {"audio", "video"}
    assert result["filesize"] == Path(result["path"]).stat().st_size
    assert not list((tmp_path / "merge").glob("track-*"))


def test_invalid_media_cleanup(monkeypatch, tmp_path):
    monkeypatch.setattr(SafeTransport, "open", lambda *a, **k: (io.BytesIO(b"<html>not a video</html>"), {}, 200, ""))
    source = record("youtube")
    with pytest.raises(MediaError):
        generate_file(source, source["metadata"]["formats"][0]["id"], tmp_path / "invalid")
    assert not (tmp_path / "invalid").exists()


def test_filenames_are_sanitized():
    assert "/" not in safe_filename("../../etc/passwd", 720, "mp4")


def test_preview_probe_reads_real_headers_without_fetching_entire_video(monkeypatch, real_media):
    from app.probe import fill_missing_formats

    class HeaderResponse(io.BytesIO):
        def read(self, size=-1):
            if self.tell():
                raise AssertionError("A readable MP4 header should not require another network chunk")
            return super().read(size)

    body = HeaderResponse(real_media["combined.mp4"] + b"\0" * (1024 * 1024))
    monkeypatch.setattr(SafeTransport, "open", lambda *args, **kwargs: (body, {}, 206, "https://cdninstagram.com/video.mp4"))
    info = {"formats": [{"format_id": "actual", "url": "https://cdninstagram.com/video.mp4", "ext": "mp4"}]}
    fill_missing_formats(info, "instagram")
    assert body.closed
    assert info["formats"][0]["width"] == 160
    assert info["formats"][0]["height"] == 90
    assert info["formats"][0]["acodec"] == "aac"


def test_tiktok_native_downloader_preserves_fresh_context(monkeypatch, real_media, tmp_path):
    from email.message import Message
    from http.cookiejar import Cookie

    from yt_dlp import YoutubeDL

    from app.tiktok_worker import download

    source = "https://www.tiktok.com/@creator/video/6718335390845095173"
    signed = "https://v16.tiktok.com/media.mp4?signature=exact%2Fvalue&expires=9999999999"
    context = {"User-Agent": "FreshExtractorAgent", "Referer": source}

    def extract(self, url, download=False):
        assert url == source and download is False
        self.cookiejar.set_cookie(
            Cookie(
                0,
                "anonymous-session",
                "fresh-only",
                None,
                False,
                ".tiktok.com",
                True,
                True,
                "/",
                True,
                True,
                int(time.time()) + 600,
                False,
                None,
                None,
                {},
                False,
            )
        )
        return {
            "id": "6718335390845095173",
            "title": "Native fixture",
            "extractor": "TikTok",
            "extractor_key": "TikTok",
            "webpage_url": source,
            "duration": 1,
            "http_headers": context,
            "formats": [
                {
                    "format_id": "play",
                    "url": signed,
                    "height": 90,
                    "width": 160,
                    "ext": "mp4",
                    "protocol": "https",
                    "vcodec": "h264",
                    "acodec": "aac",
                    "http_headers": context,
                }
            ],
        }

    calls = []

    def fetch(self, url, **kwargs):
        calls.append(url)
        assert url == signed
        headers = {k.lower(): v for k, v in kwargs["headers"].items()}
        assert headers["user-agent"] == context["User-Agent"]
        assert headers["referer"] == source
        assert any(c.name == "anonymous-session" and c.value == "fresh-only" for c in kwargs["cookiejar"])
        headers = Message()
        headers["Content-Type"] = "video/mp4"
        headers["Content-Length"] = str(len(real_media["combined.mp4"]))
        return io.BytesIO(real_media["combined.mp4"]), headers, 200, url

    monkeypatch.setattr(YoutubeDL, "extract_info", extract)
    monkeypatch.setattr(SafeTransport, "open", fetch)
    output = download({"source": source, "selector": "play", "directory": str(tmp_path), "height": 90, "hasAudio": True})
    assert calls == [signed]
    assert inspect_file(output)["streams"][0]["height"] == 90
    assert output.read_bytes() == real_media["combined.mp4"]


def test_tiktok_context_and_cdn_never_reach_frontend(memory_store, monkeypatch):
    from app.providers import providers

    private = record("tiktok")
    private["downloadStrategy"] = "yt_dlp"
    selected = next(iter(private["selections"].values()))
    selected["tracks"][0]["url"] = "https://v16.tiktok.com/private.mp4?signature=secret"
    selected["tracks"][0]["http_headers"] = {"Referer": "https://tiktok.com", "User-Agent": "ExtractorContext"}
    monkeypatch.setattr(providers["tiktok"], "extract", lambda url: private)
    response = TestClient(main.app).post("/api/v1/extract", json={"url": "https://www.tiktok.com/@creator/video/6718335390845095173"})
    assert response.status_code == 200
    for secret in ["v16.tiktok.com", "signature", "http_headers", "downloadStrategy", "ExtractorContext"]:
        assert secret not in response.text


@pytest.mark.parametrize('failure', ['missing', 'failed', 'timeout'])
def test_merge_failures_are_friendly_and_cleaned(failure, fixture_transport, monkeypatch, tmp_path):
    import app.media as media

    source = record('youtube', True)
    folder = tmp_path / failure
    if failure == 'missing':
        monkeypatch.setattr(media.shutil, 'which', lambda path: None)
    else:
        original_run = media.subprocess.run
        def fail(*args, **kwargs):
            if Path(args[0][0]).name != 'ffmpeg':
                return original_run(*args, **kwargs)
            if failure == 'timeout':
                raise subprocess.TimeoutExpired('private command', 1)
            raise subprocess.CalledProcessError(1, 'private command', stderr=b'private internal details')
        monkeypatch.setattr(media.subprocess, 'run', fail)
    with pytest.raises(MediaError) as result:
        generate_file(source, source['metadata']['formats'][0]['id'], folder)
    assert result.value.code in {'merge_unavailable', 'merge_failed', 'audio_mux_failed'}
    assert 'private' not in result.value.message
    assert not folder.exists()


def test_real_4k_separate_track_output(tmp_path, monkeypatch, real_media):
    """Local 3840x2160 fixture verifies file delivery, not live upstream access."""
    video_path = tmp_path / 'source-4k.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                    'color=c=blue:size=3840x2160:rate=2', '-t', '1', '-an',
                    '-c:v', 'libx264', '-preset', 'ultrafast', '-threads', '1',
                    '-pix_fmt', 'yuv420p', str(video_path)], check=True, timeout=30)
    payloads = {'video.mp4': video_path.read_bytes(), 'audio.m4a': real_media['audio.m4a']}
    monkeypatch.setattr(SafeTransport, 'open', lambda self, url, **kwargs:
                        (io.BytesIO(payloads[Path(url).name]), {}, 200, url))
    raw = [{'format_id': '4k', 'height': 2160, 'width': 3840, 'vcodec': 'avc1',
            'acodec': 'none', 'ext': 'mp4', 'url': 'https://fixture.invalid/video.mp4'},
           {'format_id': 'a', 'vcodec': 'none', 'acodec': 'mp4a', 'ext': 'm4a',
            'url': 'https://fixture.invalid/audio.m4a'}]
    formats, selections = normalize({'formats': raw}, 10000000)
    assert formats[0]['quality'] == '2160p 4K'
    source = {'metadata': {'title': 'Actual local 4K', 'duration': 1, 'formats': formats},
              'platform': 'youtube', 'selections': selections}
    result = generate_file(source, formats[0]['id'], tmp_path / 'output')
    measured = inspect_file(result['path'])
    video = next(stream for stream in measured['streams'] if stream['codec_type'] == 'video')
    assert (video['width'], video['height']) == (3840, 2160)
    assert any(stream['codec_type'] == 'audio' for stream in measured['streams'])
    assert Path(result['path']).stat().st_size == result['filesize'] > 0
