import os
import subprocess
import threading
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main
from app.media_errors import MediaError
from app.processing.api import sweep
from app.processing.engine import Options, inspect, process_files


@pytest.fixture(scope="module")
def uploaded_video(tmp_path_factory):
    path = tmp_path_factory.mktemp("processing-media") / "video.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=160x90:rate=10",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440",
            "-t",
            "2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(path),
        ],
        check=True,
    )
    return path


@pytest.mark.parametrize("operation", ["converter", "compressor", "trimmer", "merger", "mp3", "remove-audio", "video-to-gif", "speed"])
def test_real_essential_outputs(operation, uploaded_video, tmp_path):
    opts = (
        Options(start=0.2, end=1.2) if operation in {"trimmer", "video-to-gif"} else Options(speed=2) if operation == "speed" else Options()
    )
    result = process_files(operation, [uploaded_video] * (2 if operation == "merger" else 1), opts, tmp_path / "out", threading.Event())
    assert result["filesize"] == Path(result["path"]).stat().st_size > 0
    measured = inspect(Path(result["path"]))
    kinds = {s["codec_type"] for s in measured["streams"]}
    if operation == "mp3":
        assert kinds == {"audio"}
    else:
        assert "video" in kinds
    if operation == "remove-audio":
        assert "audio" not in kinds
    if operation in {"trimmer", "speed"}:
        assert 0.8 <= measured["duration"] <= 1.3
    if operation == "merger":
        assert 3.8 <= measured["duration"] <= 4.3


@pytest.mark.parametrize("fmt", ["mov", "webm"])
def test_actual_conversion_formats(uploaded_video, tmp_path, fmt):
    result = process_files("converter", [uploaded_video], Options(output_format=fmt), tmp_path / fmt, threading.Event())
    assert Path(result["path"]).suffix == "." + fmt
    assert result["metadata"]["duration"] > 0


def test_cancellation_removes_output(uploaded_video, tmp_path):
    cancel = threading.Event()
    cancel.set()
    with pytest.raises(MediaError):
        process_files("converter", [uploaded_video], Options(), tmp_path / "out", cancel)
    assert not (tmp_path / "out").exists()


def test_invalid_and_oversized_inputs(uploaded_video, tmp_path, monkeypatch):
    invalid = tmp_path / "invalid.mp4"
    invalid.write_bytes(b"not media")
    with pytest.raises(MediaError):
        inspect(invalid)
    with pytest.raises(MediaError):
        process_files("converter", [], Options(), tmp_path / "out", threading.Event())
    monkeypatch.setattr(main.settings, "max_file_bytes", 10)
    with pytest.raises(MediaError) as failure:
        process_files("converter", [uploaded_video], Options(), tmp_path / "out", threading.Event())
    assert failure.value.code == "file_too_large"


def test_remote_playlist_cannot_be_probed(tmp_path):
    path = tmp_path / "playlist.mp4"
    path.write_text("#EXTM3U\nhttp://127.0.0.1/secret\n")
    with pytest.raises(MediaError):
        inspect(path)


def test_feature_can_be_disabled(monkeypatch):
    monkeypatch.setattr(main.settings, "processing_enabled", False)
    assert TestClient(main.app).get("/processing/capabilities").status_code == 503


def test_binary_upload_job_and_protected_file(memory_store, monkeypatch, uploaded_video):
    monkeypatch.setattr(main.settings, "processing_enabled", True)
    with TestClient(main.app) as client:
        response = client.post(
            "/processing/uploads", content=uploaded_video.read_bytes(), headers={"Content-Type": "application/octet-stream"}
        )
        assert response.status_code == 200, response.text
        item = response.json()
        assert item["filesize"] == uploaded_video.stat().st_size and "path" not in response.text
        created = client.post("/processing/jobs", json={"operation": "remove-audio", "upload_ids": [item["uploadId"]]})
        assert created.status_code == 202, created.text
        token = created.json()["jobId"]
        for _ in range(100):
            job = client.get(f"/processing/jobs/{token}").json()
            if job.get("status") in {"ready", "error"}:
                break
            time.sleep(0.05)
        assert job["status"] == "ready", job
        saved = client.get(job["downloadUrl"])
        assert saved.status_code == 200 and len(saved.content) == job["filesize"]
        assert client.get("/processing/files/" + "f" * 32).status_code == 410
        assert client.post(f"/processing/jobs/{token}/cancel").json()["status"] == "cancelled"
        assert client.get(job["downloadUrl"]).status_code == 410


def test_upload_validation_and_expiry(memory_store, monkeypatch):
    monkeypatch.setattr(main.settings, "processing_enabled", True)
    with TestClient(main.app) as client:
        headers = {"Content-Type": "application/octet-stream"}
        assert client.post("/processing/uploads", content=b"", headers=headers).status_code == 400
        assert client.post("/processing/uploads", content=b"invalid", headers=headers).status_code == 422
        monkeypatch.setattr(main.settings, "max_file_bytes", 2)
        assert client.post("/processing/uploads", content=b"123", headers=headers).status_code == 413
        assert client.get("/processing/jobs/" + "f" * 32).status_code == 410
        assert client.post("/processing/jobs", json={"operation": "converter", "upload_ids": ["../../etc/passwd"]}).status_code == 400


def test_stale_cleanup_preserves_active_and_symlinks(tmp_path):
    old = tmp_path / ("a" * 32)
    old.mkdir()
    os.utime(old, (0, 0))
    active = tmp_path / ("b" * 32)
    active.mkdir()
    link = tmp_path / ("c" * 32)
    link.symlink_to(active, target_is_directory=True)
    sweep(tmp_path)
    assert not old.exists() and active.is_dir() and link.is_symlink()


def test_timeout_cleans_output(uploaded_video, monkeypatch, tmp_path):
    monkeypatch.setattr(main.settings, "download_timeout_seconds", 0.001)
    with pytest.raises(MediaError) as failure:
        process_files("converter", [uploaded_video], Options(), tmp_path / "out", threading.Event())
    assert failure.value.code in {"processing_timeout", "processing_failed"}
    assert not (tmp_path / "out").exists()


def test_processing_slots_are_shared_with_downloaders(memory_store, monkeypatch, uploaded_video):
    monkeypatch.setattr(main.settings, "processing_enabled", True)
    with TestClient(main.app) as client:
        item = client.post(
            "/processing/uploads", content=uploaded_video.read_bytes(), headers={"Content-Type": "application/octet-stream"}
        ).json()
        for index in range(main.settings.max_concurrent_jobs):
            memory_store.data[f"download-slot:{index}"] = ("another-job", time.time() + 60)
        response = client.post("/processing/jobs", json={"operation": "converter", "upload_ids": [item["uploadId"]]})
        assert response.status_code == 503 and response.json()["error"]["code"] == "server_busy"


def test_processing_invalid_settings_and_unsupported_operation(memory_store, monkeypatch, uploaded_video):
    monkeypatch.setattr(main.settings, "processing_enabled", True)
    with TestClient(main.app) as client:
        item = client.post(
            "/processing/uploads", content=uploaded_video.read_bytes(), headers={"Content-Type": "application/octet-stream"}
        ).json()
        base = {"operation": "converter", "upload_ids": [item["uploadId"]]}
        assert client.post("/processing/jobs", json={**base, "options": {"output_format": "mp4;rm -rf /"}}).status_code == 400
        assert client.post("/processing/jobs", json={**base, "path": "/etc/passwd"}).status_code == 400
        assert client.post("/processing/jobs", json={**base, "operation": "not-implemented"}).status_code == 501
        assert client.post("/processing/jobs", content=b"x" * 8193).status_code == 413


def test_processing_rate_limit(memory_store, monkeypatch, caplog):
    import logging

    caplog.set_level(logging.INFO, logger="socialvid.api")
    monkeypatch.setattr(main.settings, "processing_enabled", True)
    monkeypatch.setattr(main.settings, "rate_limit_per_minute", 1)
    with TestClient(main.app) as client:
        response = client.post("/processing/jobs", json={})
        assert response.status_code == 400
        response = client.post("/processing/jobs", json={})
        assert response.status_code == 429
        assert response.json()["error"]["code"] == "rate_limited"
        assert '"error_category": "rate_limited"' in caplog.text


def test_unavailable_binaries_return_friendly_error(uploaded_video, monkeypatch, tmp_path):
    from app.processing import engine

    original = engine.shutil.which
    monkeypatch.setattr(engine.shutil, "which", lambda path: None if path == main.settings.ffmpeg_path else original(path))
    with pytest.raises(MediaError) as failure:
        process_files("converter", [uploaded_video], Options(), tmp_path / "out", threading.Event())
    assert failure.value.code == "processing_unavailable"
    assert not (tmp_path / "out").exists()


def test_concurrent_uploads_reserve_actual_processing_slots(memory_store, monkeypatch, uploaded_video):
    monkeypatch.setattr(main.settings, "processing_enabled", True)
    # Another upload can coexist when no processing job has reserved output.
    memory_store.data["processing-upload-slot:0"] = ("other-upload", time.time() + 60)
    with TestClient(main.app) as client:
        response = client.post(
            "/processing/uploads", content=uploaded_video.read_bytes(), headers={"Content-Type": "application/octet-stream"}
        )
        assert response.status_code == 200


@pytest.mark.parametrize("stage", ["upload", "job"])
def test_storage_admission_is_distinct_from_job_capacity(memory_store, monkeypatch, uploaded_video, caplog, stage):
    import logging

    caplog.set_level(logging.INFO, logger="socialvid.api")
    monkeypatch.setattr(main.settings, "processing_enabled", True)
    with TestClient(main.app) as client:
        headers = {"Content-Type": "application/octet-stream"}
        if stage == "job":
            item = client.post("/processing/uploads", content=uploaded_video.read_bytes(), headers=headers).json()
        monkeypatch.setattr(main.settings, "max_storage_bytes", 1)
        if stage == "upload":
            response = client.post("/processing/uploads", content=uploaded_video.read_bytes(), headers=headers)
        else:
            response = client.post("/processing/jobs", json={"operation": "converter", "upload_ids": [item["uploadId"]]})
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "storage_busy"
        assert '"error_category": "storage_busy"' in caplog.text
        assert not any(key.startswith(("processing-upload-slot:", "download-slot:")) for key in memory_store.data)
