import io
import shutil
import subprocess
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main
from app.audio import audio_catalog, download_plan, language_code, public_audio
from app.formats import normalize
from app.media import generate_file, safe_filename
from app.media_errors import MediaError
from app.probe import inspect_file
from app.provider_health import baseline
from app.transport import SafeTransport


def video(identifier="v", **extra):
    return {
        "format_id": identifier,
        "url": f"https://fixture.invalid/{identifier}.mp4",
        "height": 90,
        "width": 160,
        "vcodec": "h264",
        "acodec": "none",
        "ext": "mp4",
        "protocol": "https",
        **extra,
    }


def audio(code="en", identifier=None, **extra):
    identifier = identifier or code or "unknown"
    return {
        "format_id": identifier,
        "url": f"https://fixture.invalid/{identifier}.{extra.get('ext', 'm4a')}",
        "ext": "m4a",
        "vcodec": "none",
        "acodec": "aac",
        "abr": 128,
        "language": code,
        "protocol": "https",
        **extra,
    }


def source(formats, platform="youtube", merge_available=True):
    info = {"formats": formats}
    public, selections = normalize(info, 10000000, merge_available, platform)
    return {
        "metadata": {
            "title": "Audio integration fixture",
            "formats": public,
            "thumbnailSource": None,
            "platform": platform,
            **public_audio(selections),
        },
        "platform": platform,
        "selections": selections,
        "source": "fixture",
    }


def ids(record):
    return [t["id"] for t in record["metadata"]["audio_tracks"]]


def plan(record, mode="single", selected=None):
    return download_plan(record, record["metadata"]["formats"][0]["id"], mode, selected)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("eng", "en"),
        ("hin", "hi"),
        ("en_US", "en-us"),
        ("fr-CA", "fr-ca"),
        ("fre", "fr"),
        ("deu", "de"),
        ("in", "id"),
        ("en-US-desc", "en-us"),
        (None, None),
        ("", None),
        ("und", None),
        ("mul", None),
        ("not a language", None),
    ],
)
def test_language_normalization(raw, expected):
    assert language_code(raw) == expected


@pytest.mark.parametrize(
    "code,name",
    [
        ("en", "English"),
        ("hi", "Hindi"),
        ("ar", "Arabic"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("pt", "Portuguese"),
        ("id", "Indonesian"),
        ("bn", "Bengali"),
        ("ur", "Urdu"),
        ("de", "German"),
        ("ja", "Japanese"),
        ("ko", "Korean"),
        ("tr", "Turkish"),
    ],
)
def test_names_only_for_source_languages(code, name):
    record = source([video(), audio(code)])
    assert len(record["metadata"]["audio_tracks"]) == 1
    assert record["metadata"]["audio_tracks"][0]["language_name"] == name
    assert record["metadata"]["supports_dual_audio"] is False


def test_unknown_language_fallback_never_guesses_english():
    record = source([video(acodec="aac")])
    track = record["metadata"]["audio_tracks"][0]
    assert track["language_name"] == "Unknown" and track["language_code"] is None
    assert track["label"] == "Original" and track["is_original"] is False
    assert not record["metadata"]["supports_dual_audio"]


def test_default_original_and_descriptive_evidence():
    tracks = audio_catalog(
        [
            audio("en", format_note="English original", language_preference=10),
            audio("hi", format_note="Hindi (default)", language_preference=5),
            audio("en-desc", "description", format_note="English descriptive", language_preference=-10),
        ],
        "youtube",
    )
    assert tracks[0]["is_original"] and not tracks[0]["is_default"]
    assert tracks[1]["is_default"] and not tracks[1]["is_original"]
    assert tracks[2]["is_descriptive"] and tracks[2]["language_code"] == "en"
    record = source([video(), audio("en", is_original=True), audio("hi", is_default=True)])
    assert plan(record)["selected_audio"][0]["language_code"] == "hi"


def test_youtube_preference_numbers_not_assumed_for_other_providers():
    track = audio_catalog([audio("hi", language_preference=10)], "instagram")[0]
    assert track["is_original"] is False


def test_audio_bitrate_variants_not_language_choices_and_no_subtitle_languages():
    record = source(
        [
            video(),
            audio("en", "aac", abr=128),
            audio("en", "low", abr=64),
            audio("en", "opus", ext="webm", acodec="opus"),
            audio("hi", has_drm=True),
            audio("ar", protocol="m3u8_native"),
        ]
    )
    tracks = record["metadata"]["audio_tracks"]
    assert [t["language_code"] for t in tracks] == ["en"]
    assert tracks[0]["bitrate"] == 128000
    assert plan(record)["format"]["extension"] == "mp4"
    assert len(plan(record)["tracks"]) == 2


def test_unknown_codec_variants_not_fake_alternate_tracks():
    record = source([video(), audio(None, "one"), audio(None, "two", abr=64)])
    assert len(ids(record)) == 1
    assert not record["metadata"]["supports_dual_audio"]


@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_inventory_one_two_or_more_tracks(count):
    record = source([video()] + [audio(code) for code in ["en", "hi", "ar", "es"][:count]])
    assert len(ids(record)) == count
    assert record["metadata"]["supports_dual_audio"] == (count > 1)
    if count >= 2:
        selected = plan(record, "dual" if count == 2 else "multi", ids(record))
        assert len(selected["audio_maps"]) == count
        assert selected["format"]["extension"] == "mp4"


def test_audio_id_validation_and_duplicate_languages():
    record = source([video(), audio("en"), audio("hi"), audio("en-desc", "descriptive", is_descriptive=True)])
    with pytest.raises(MediaError) as failure:
        plan(record, "dual", [ids(record)[0], "invented"])
    assert failure.value.code == "second_audio_track_unavailable"
    with pytest.raises(MediaError) as failure:
        plan(record, "single", ["invented"])
    assert failure.value.code == "audio_track_unavailable"
    with pytest.raises(MediaError) as failure:
        plan(record, "dual", [ids(record)[0]] * 2)
    assert failure.value.code == "duplicate_audio_track"
    with pytest.raises(MediaError) as failure:
        plan(record, "dual", [ids(record)[0], ids(record)[2]])
    assert failure.value.code == "duplicate_audio_language"


def test_dual_audio_not_available_with_one_track_or_without_ffmpeg():
    record = source([video(acodec="aac", language="en")], merge_available=False)
    with pytest.raises(MediaError) as failure:
        plan(record, "dual", [ids(record)[0], "other"])
    assert failure.value.code == "dual_audio_not_supported"
    record = source([video(), audio("en")])
    with pytest.raises(MediaError) as failure:
        plan(record, "dual", [ids(record)[0], "other"])
    assert failure.value.code == "dual_audio_not_supported"


def test_container_and_filesize_follow_audio_selection():
    record = source([video(), audio("en"), audio("hi", ext="webm", acodec="opus")])
    fmt = record["metadata"]["formats"][0]
    assert fmt["audio_containers"][ids(record)[0]] == "mp4"
    assert fmt["audio_containers"][ids(record)[1]] == "mkv"
    assert plan(record, "dual", ids(record))["format"]["extension"] == "mkv"
    combined = source([video(acodec="aac", language="en", filesize=1234)])
    fmt = combined["metadata"]["formats"][0]
    assert fmt["filesize"] is None and fmt["estimatedFilesize"] == 1234


def test_filename_languages_modes_length_and_safety():
    record = source([video(), audio("en"), audio("hi")])
    tracks = record["metadata"]["audio_tracks"]
    name = safe_filename("../../My Video", 1080, "mp4", tracks, "dual")
    assert name == "My-Video-1080p-english-hindi-dual-audio-socialviddownloader.mp4"
    assert safe_filename("Clip", 1080, "mp4", [tracks[1]]) == "Clip-1080p-hindi-socialviddownloader.mp4"
    assert len(safe_filename("x" * 1000, 2160, "mkv", tracks * 4, "multi")) < 255
    assert "/" not in name


@pytest.fixture(scope="module")
def media_files(tmp_path_factory):
    assert shutil.which("ffmpeg") and shutil.which("ffprobe")
    folder = tmp_path_factory.mktemp("audio-real-streams")
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=160x90:rate=5",
            "-t",
            "1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(folder / "v.mp4"),
        ],
        check=True,
    )
    for code, frequency in [("en", 440), ("hi", 660), ("ar", 880)]:
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency={frequency}",
                "-t",
                "1",
                "-c:a",
                "aac",
                str(folder / f"{code}.m4a"),
            ],
            check=True,
        )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(folder / "hi.m4a"), "-c:a", "libopus", str(folder / "hi-opus.webm")], check=True
    )
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(folder / "v.mp4"),
            "-i",
            str(folder / "en.m4a"),
            "-i",
            str(folder / "hi.m4a"),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-map",
            "2:a",
            "-c",
            "copy",
            "-metadata:s:a:0",
            "language=eng",
            "-metadata:s:a:1",
            "language=hin",
            "-movflags",
            "+faststart",
            str(folder / "embedded.mp4"),
        ],
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(folder / "hi.m4a"),
            "-c",
            "copy",
            "-metadata:s:a:0",
            "language=hin",
            str(folder / "wrong-en.m4a"),
        ],
        check=True,
    )
    return {p.name: p.read_bytes() for p in folder.iterdir()}


@pytest.fixture
def media_transport(monkeypatch, media_files):
    monkeypatch.setattr(SafeTransport, "open", lambda self, url, **kwargs: (io.BytesIO(media_files[Path(url).name]), {}, 200, url))


@pytest.mark.parametrize("mode,codes", [("single", ["hi"]), ("dual", ["en", "hi"]), ("multi", ["en", "hi", "ar"])])
def test_real_mux_stream_counts_languages_and_exact_selected_audio(mode, codes, media_transport, media_files, tmp_path):
    record = source([video(), audio("en", is_original=True, is_default=True), audio("hi"), audio("ar")])
    chosen = [t for code in codes for t in record["metadata"]["audio_tracks"] if t["language_code"] == code]
    result = generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / mode, mode, [t["id"] for t in chosen])
    measured = inspect_file(result["path"])
    assert len([s for s in measured["streams"] if s["codec_type"] == "video"]) == 1
    streams = [s for s in measured["streams"] if s["codec_type"] == "audio"]
    assert [s["tags"]["language"] for s in streams] == [{"en": "eng", "hi": "hin", "ar": "ara"}[c] for c in codes]
    assert len(streams) == len(codes)
    assert [bool(s["disposition"]["default"]) for s in streams] == [True] + [False] * (len(codes) - 1)
    assert result["filesize"] == Path(result["path"]).stat().st_size
    assert not list(Path(result["path"]).parent.glob("track-*"))
    # Compare the compressed packets with each source: audio is selected, not mixed or transcoded.
    for index, code in enumerate(codes):
        source_path = tmp_path / f"{code}.m4a"
        source_path.write_bytes(media_files[f"{code}.m4a"])
        args = ["ffmpeg", "-v", "error", "-i"]
        saved = subprocess.check_output(args + [result["path"], "-map", f"0:a:{index}", "-c:a", "copy", "-f", "adts", "pipe:1"])
        original = subprocess.check_output(args + [str(source_path), "-map", "0:a:0", "-c:a", "copy", "-f", "adts", "pipe:1"])
        assert saved == original


def test_mkv_codec_fallback_verified(media_transport, tmp_path):
    record = source([video(), audio("en"), audio("hi", "hi-opus", ext="webm", acodec="opus")])
    result = generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / "mkv", "dual", ids(record))
    assert result["extension"] == "mkv"
    streams = [s for s in inspect_file(result["path"])["streams"] if s["codec_type"] == "audio"]
    assert [s["codec_name"] for s in streams] == ["aac", "opus"]
    assert [s["tags"]["language"] for s in streams] == ["eng", "hin"]


def test_embedded_streams_probed_and_selectable_without_duplicate_downloads(media_transport, tmp_path, media_files):
    from app.probe import fill_missing_formats

    info = {"formats": [video("embedded", acodec=None)]}
    fill_missing_formats(info, "facebook")
    assert len(info["formats"][0]["audio_streams"]) == 2
    record = source(info["formats"], "facebook")
    selected = plan(record, "dual", ids(record))
    assert selected["audio_maps"] == [(0, 0), (0, 1)] and len(selected["tracks"]) == 1
    result = generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / "embedded", "single", [ids(record)[1]])
    streams = [s for s in inspect_file(result["path"])["streams"] if s["codec_type"] == "audio"]
    assert len(streams) == 1 and streams[0]["tags"]["language"] == "hin"
    dual = generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / "embedded-dual", "dual", ids(record))
    assert len([s for s in inspect_file(dual["path"])["streams"] if s["codec_type"] == "audio"]) == 2


def test_final_verification_blocks_false_ready_and_cleans_up(media_transport, monkeypatch, tmp_path):
    from app import media

    record = source([video(), audio("en"), audio("hi")])
    inspect = media.inspect_file
    monkeypatch.setattr(
        media, "inspect_file", lambda path, **kwargs: {**inspect(path, **kwargs), "streams": inspect(path, **kwargs)["streams"][:2]}
    )
    with pytest.raises(MediaError) as failure:
        generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / "bad", "dual", ids(record))
    assert failure.value.code == "audio_mux_failed" and not (tmp_path / "bad").exists()


@pytest.mark.parametrize(
    "platform,url",
    [
        ("youtube", "https://youtube.com/watch?v=BaW_jenozKc"),
        ("facebook", "https://facebook.com/watch/?v=123"),
        ("instagram", "https://instagram.com/p/Example123/"),
        ("tiktok", "https://tiktok.com/@creator/video/123456"),
        ("snapchat", "https://snapchat.com/spotlight/abc123"),
    ],
)
def test_audio_pipeline_shared_by_all_providers(platform, url, memory_store, monkeypatch, media_transport):
    record = source([video(), audio("en"), audio("hi")], platform)
    monkeypatch.setattr(main.providers[platform], "extract", lambda url: record)
    with TestClient(main.app) as client:
        extracted = client.post("/api/v1/extract", json={"url": url}).json()
        assert extracted["supports_dual_audio"] and len(extracted["audio_tracks"]) == 2
        assert "fixture.invalid" not in str(extracted) and "sources" not in str(extracted)
        job = client.post(
            "/api/v1/download",
            json={
                "sessionId": extracted["sessionId"],
                "formatId": extracted["formats"][0]["id"],
                "audio_mode": "dual",
                "audio_track_ids": ids(record),
            },
        )
        assert job.status_code == 202
        token = job.json()["jobId"]
        for _ in range(100):
            result = client.get("/api/v1/jobs/" + token).json()
            if result["status"] in {"ready", "error"}:
                break
            time.sleep(0.02)
        assert result["status"] == "ready", result
        assert result["audio_mode"] == "dual" and len(result["audio_tracks"]) == 2
        assert client.get("/api/v1/files/" + token).headers["content-type"] == "video/mp4"
        status = memory_store.data["provider-health:" + platform][0]
        assert status["supports_multiple_audio_tracks"] and status["supports_language_metadata"] and status["supports_dual_audio_mux"]


def test_invalid_audio_rejected_before_a_job_is_created(memory_store):
    record = source([video(), audio("en"), audio("hi")])
    token = "a" * 32
    memory_store.data["session:" + token] = (record, time.time() + 60)
    with TestClient(main.app) as client:
        response = client.post(
            "/api/v1/download",
            json={
                "sessionId": token,
                "formatId": record["metadata"]["formats"][0]["id"],
                "audio_mode": "dual",
                "audio_track_ids": [ids(record)[0], "../../ffmpeg"],
            },
        )
    assert response.status_code == 400 and response.json()["error"]["code"] == "second_audio_track_unavailable"
    assert not any(key.startswith("job:") for key in memory_store.data)


def test_unknown_capability_not_advertised_as_verified():
    assert baseline("youtube")["supports_dual_audio_mux"] is None


def test_oversized_audio_excluded():
    record = source([video(), audio("en"), audio("hi", filesize=20000000)])
    assert len(ids(record)) == 1


def test_mux_language_mismatch_is_not_success(media_transport, monkeypatch, tmp_path):
    from app import media

    record = source([video(), audio("en"), audio("hi")])
    inspect = media.inspect_file

    def wrong_language(path, **kwargs):
        result = inspect(path, **kwargs)
        if not kwargs:
            next(s for s in result["streams"] if s["codec_type"] == "audio")["tags"]["language"] = "fra"
        return result

    monkeypatch.setattr(media, "inspect_file", wrong_language)
    with pytest.raises(MediaError) as failure:
        generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / "wrong-language", "dual", ids(record))
    assert failure.value.code == "audio_mux_failed"
    assert not (tmp_path / "wrong-language").exists()


def test_output_size_budget_and_duration_enforced(media_transport, monkeypatch, tmp_path):
    from app.config import settings

    record = source([video(), audio("en"), audio("hi")])
    monkeypatch.setattr(settings, "max_file_bytes", 10)
    with pytest.raises(MediaError) as failure:
        generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / "size", "dual", ids(record))
    assert failure.value.code == "file_too_large" and not (tmp_path / "size").exists()
    monkeypatch.setattr(settings, "max_file_bytes", 10000000)
    monkeypatch.setattr(settings, "max_duration_seconds", 0.1)
    with pytest.raises(MediaError) as failure:
        generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / "duration", "dual", ids(record))
    assert failure.value.code == "video_too_long" and not (tmp_path / "duration").exists()


def test_primary_audio_order_is_preserved(media_transport, tmp_path):
    record = source([video(), audio("en", is_default=True), audio("hi")])
    result = generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / "reverse", "dual", list(reversed(ids(record))))
    streams = [s for s in inspect_file(result["path"])["streams"] if s["codec_type"] == "audio"]
    assert [s["tags"]["language"] for s in streams] == ["hin", "eng"]
    assert [bool(s["disposition"]["default"]) for s in streams] == [True, False]
    assert result["audio_tracks"][0]["is_default"] and not result["audio_tracks"][0]["source_is_default"]
    assert not result["audio_tracks"][1]["is_default"] and result["audio_tracks"][1]["source_is_default"]
    assert "Default" in result["audio_tracks"][0]["label"] and "Default" not in result["audio_tracks"][1]["label"]


def test_native_tiktok_downloads_selected_inputs_without_delegating_network_to_ffmpeg(monkeypatch, media_files, tmp_path):
    from email.message import Message

    from yt_dlp import YoutubeDL

    from app.tiktok_worker import download

    public_url = "https://www.tiktok.com/@creator/video/6718335390845095173"
    raw = [video(), audio("en"), audio("hi")]
    for fmt in raw:
        fmt["url"] = fmt["url"].replace("fixture.invalid", "v16.tiktok.com")
        fmt["http_headers"] = {"User-Agent": "FreshExtractorAgent", "Referer": public_url}
    info = {
        "id": "6718335390845095173",
        "title": "Native multilingual fixture",
        "extractor": "TikTok",
        "extractor_key": "TikTok",
        "webpage_url": public_url,
        "duration": 1,
        "formats": raw,
    }
    monkeypatch.setattr(YoutubeDL, "extract_info", lambda *args, **kwargs: info)
    calls = []

    def fetch(self, url, **kwargs):
        assert self.platform == "tiktok" and kwargs["cookiejar"] is not None
        assert kwargs["headers"]["User-Agent"] == "FreshExtractorAgent"
        data = media_files[Path(url).name]
        headers = Message()
        headers["Content-Type"] = "video/mp4"
        headers["Content-Length"] = str(len(data))
        calls.append(url)
        return io.BytesIO(data), headers, 200, url

    monkeypatch.setattr(SafeTransport, "open", fetch)
    outputs = download(
        {
            "source": public_url,
            "selector": "v",
            "directory": str(tmp_path),
            "height": 90,
            "hasAudio": True,
            "inputs": [
                {"format_id": f["format_id"], "extension": f["ext"], "language": f.get("language"), "height": f.get("height")} for f in raw
            ],
        }
    )
    assert len(outputs) == 3 and len(calls) == 3
    assert [p.read_bytes() for p in outputs] == [media_files["v.mp4"], media_files["en.m4a"], media_files["hi.m4a"]]


def test_native_tiktok_fresh_language_change_is_rejected(monkeypatch, tmp_path):
    from yt_dlp import YoutubeDL

    from app.tiktok_worker import download

    monkeypatch.setattr(
        YoutubeDL, "extract_info", lambda *args, **kwargs: {"id": "sample", "formats": [video(acodec="aac", language="fr")]}
    )
    with pytest.raises(MediaError) as failure:
        download(
            {
                "source": "https://www.tiktok.com/@creator/video/6718335390845095173",
                "selector": "v",
                "directory": str(tmp_path),
                "height": 90,
                "hasAudio": True,
                "inputs": [{"format_id": "v", "height": 90, "language": "en", "extension": "mp4"}],
            }
        )
    assert failure.value.code == "audio_track_unavailable"


def test_native_launcher_receives_only_session_selected_ids(monkeypatch, tmp_path):
    from app import tiktok_download

    record = source([video(), audio("en"), audio("hi")], "tiktok")
    selection = plan(record, "dual", ids(record))
    sent = {}

    class Process:
        returncode = 0

        def communicate(self, data, timeout):
            import json

            sent.update(json.loads(data))
            paths = []
            for index, item in enumerate(selection["tracks"]):
                path = tmp_path / f"native-{index}.{item['ext']}"
                path.write_bytes(b"fixture")
                paths.append(str(path))
            return json.dumps({"success": True, "paths": paths}).encode(), b""

    monkeypatch.setattr(tiktok_download.subprocess, "Popen", lambda *args, **kwargs: Process())
    outputs = tiktok_download.native_download(record, record["metadata"]["formats"][0]["id"], tmp_path, selection)
    assert [item["format_id"] for item in sent["inputs"]] == ["v", "en", "hi"]
    assert len(outputs) == 3 and "url" not in str(sent)


def test_alternate_combined_audio_uses_smallest_source_video():
    record = source(
        [
            video("english", acodec="aac", language="en", is_original=True),
            video("hindi-hd", acodec="aac", language="hi", height=1080, abr=130),
            video("hindi-small", acodec="aac", language="hi", height=90, abr=128),
        ]
    )
    smallest = next(fmt for fmt in record["metadata"]["formats"] if fmt["height"] == 90)
    chosen = download_plan(record, smallest["id"], "dual", ids(record))
    assert len(chosen["tracks"]) == 2
    assert chosen["tracks"][1]["format_id"] == "hindi-small"


def test_embedded_unknown_track_does_not_inherit_first_stream_language_or_flags():
    record = source(
        [
            video(
                acodec="aac",
                language="en",
                is_default=True,
                is_original=True,
                abr=128,
                audio_streams=[
                    {"codec_name": "aac", "tags": {"language": "eng"}, "disposition": {"default": 1}},
                    {"codec_name": "aac", "tags": {}, "disposition": {"default": 0}},
                ],
            )
        ]
    )
    tracks = record["metadata"]["audio_tracks"]
    assert tracks[0]["language_code"] == "en" and tracks[0]["is_original"] and tracks[0]["is_default"]
    assert tracks[1]["language_code"] is None and not tracks[1]["is_original"] and not tracks[1]["is_default"]
    assert tracks[1]["language_name"] == "Unknown" and tracks[1]["bitrate"] is None


def test_known_codec_source_still_exposes_embedded_audio_when_probed(media_transport):
    from app.probe import fill_missing_formats

    info = {"formats": [video("embedded", acodec="aac")]}
    fill_missing_formats(info, "instagram")
    assert len(info["formats"][0]["audio_streams"]) == 2
    record = source(info["formats"], "instagram")
    assert [t["language_code"] for t in record["metadata"]["audio_tracks"]] == ["en", "hi"]
    assert record["metadata"]["supports_dual_audio"]


def test_unidentified_progressive_variant_not_advertised_as_an_extra_language():
    record = source([video("tagged", acodec="aac", language="en"), video("untagged", acodec="aac", height=360)])
    assert [t["language_code"] for t in record["metadata"]["audio_tracks"]] == ["en"]
    assert not record["metadata"]["supports_dual_audio"]


def test_unsupported_audio_not_mislabeled_as_silent_video():
    with pytest.raises(MediaError) as failure:
        source([video(acodec="ac4")])
    assert failure.value.code == "no_supported_formats"


def test_unsupported_container_returns_a_safe_error():
    from app.audio import output_container

    with pytest.raises(MediaError) as failure:
        output_container(video(), [{"acodec": "ac4"}])
    assert failure.value.code == "unsupported_container"
    assert "ffmpeg" not in failure.value.message.lower()


def test_subtitles_and_top_level_language_do_not_invent_audio_languages():
    formats, selections = normalize(
        {
            "formats": [video(acodec="aac")],
            "language": "en",
            "subtitles": {"hi": [{"url": "https://fixture.invalid/caption.vtt"}]},
            "automatic_captions": {"ar": []},
        },
        10000000,
        platform="youtube",
    )
    tracks = public_audio(selections)["audio_tracks"]
    assert len(tracks) == 1 and tracks[0]["language_code"] is None
    assert tracks[0]["language_name"] == "Unknown" and tracks[0]["label"] == "Original"
    assert not formats[0]["supports_dual_audio"]


def test_conflicting_source_language_is_rejected_before_relabeling(monkeypatch, media_files, tmp_path):
    record = source([video(), audio("en")])

    def fetch(self, url, **kwargs):
        name = "wrong-en.m4a" if Path(url).name == "en.m4a" else Path(url).name
        return io.BytesIO(media_files[name]), {}, 200, url

    monkeypatch.setattr(SafeTransport, "open", fetch)
    with pytest.raises(MediaError) as failure:
        generate_file(record, record["metadata"]["formats"][0]["id"], tmp_path / "wrong-input")
    assert failure.value.code == "audio_track_unavailable" and not (tmp_path / "wrong-input").exists()
